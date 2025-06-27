import pytest
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    JWTManager,
    PasswordManager,
    AuthService,
    get_jwt_manager,
    extract_token,
    get_current_user,
    auth_required,
    admin_required,
    user_required
)
from app.models.user import User
from app.models.admin import Admin


class TestJWTManager:
    """Тесты для JWTManager"""
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.secret_key = "test_secret_key"
        self.jwt_manager = JWTManager(self.secret_key)
    
    def test_jwt_manager_initialization(self):
        """Тест инициализации JWTManager"""
        assert self.jwt_manager.secret_key == self.secret_key
        assert self.jwt_manager.algorithm == "HS256"
        
        custom_manager = JWTManager("key", "HS512")
        assert custom_manager.algorithm == "HS512"
    
    def test_generate_token_default_expiration(self):
        """Тест генерации токена с дефолтным временем истечения"""
        user_id = 123
        user_type = "user"
        
        token = self.jwt_manager.generate_token(user_id, user_type)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        assert payload["user_id"] == user_id
        assert payload["user_type"] == user_type
        assert "exp" in payload
        assert "iat" in payload
    
    def test_generate_token_custom_expiration(self):
        """Тест генерации токена с кастомным временем истечения"""
        user_id = 456
        user_type = "admin"
        expires_in = 7200
        
        token = self.jwt_manager.generate_token(user_id, user_type, expires_in)
        
        payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        
        time_diff = (exp_time - iat_time).total_seconds()
        assert abs(time_diff - expires_in) < 1
    
    def test_decode_token_success(self):
        """Тест успешного декодирования токена"""
        user_id = 789
        user_type = "user"
        
        token = self.jwt_manager.generate_token(user_id, user_type)
        payload = self.jwt_manager.decode_token(token)
        
        assert payload["user_id"] == user_id
        assert payload["user_type"] == user_type
    
    def test_decode_token_expired(self):
        """Тест декодирования истекшего токена"""
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        payload = {
            "user_id": 123,
            "user_type": "user",
            "exp": past_time,
            "iat": past_time - timedelta(hours=1)
        }
        
        expired_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        with pytest.raises(ValueError, match="Токен истек"):
            self.jwt_manager.decode_token(expired_token)
    
    def test_decode_token_invalid(self):
        """Тест декодирования недействительного токена"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(ValueError, match="Недействительный токен"):
            self.jwt_manager.decode_token(invalid_token)
    
    def test_decode_token_wrong_secret(self):
        """Тест декодирования токена с неправильным секретом"""
        token = jwt.encode({"user_id": 123}, "wrong_secret", algorithm="HS256")
        
        with pytest.raises(ValueError, match="Недействительный токен"):
            self.jwt_manager.decode_token(token)


class TestPasswordManager:
    """Тесты для PasswordManager"""
    
    def test_hash_password(self):
        """Тест хеширования пароля"""
        password = "test_password_123"
        hashed = PasswordManager.hash_password(password)
        
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith('$2b$')
    
    def test_hash_password_different_hashes(self):
        """Тест что одинаковые пароли дают разные хеши (из-за соли)"""
        password = "same_password"
        hash1 = PasswordManager.hash_password(password)
        hash2 = PasswordManager.hash_password(password)
        
        assert hash1 != hash2
        assert PasswordManager.verify_password(password, hash1)
        assert PasswordManager.verify_password(password, hash2)
    
    def test_verify_password_success(self):
        """Тест успешной проверки пароля"""
        password = "correct_password"
        hashed = PasswordManager.hash_password(password)
        
        assert PasswordManager.verify_password(password, hashed) is True
    
    def test_verify_password_failure(self):
        """Тест неудачной проверки пароля"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = PasswordManager.hash_password(password)
        
        assert PasswordManager.verify_password(wrong_password, hashed) is False
    
    def test_hash_verify_unicode_password(self):
        """Тест хеширования и проверки пароля с unicode символами"""
        password = "пароль_с_русскими_символами_123"
        hashed = PasswordManager.hash_password(password)
        
        assert PasswordManager.verify_password(password, hashed) is True
        assert PasswordManager.verify_password("неправильный_пароль", hashed) is False


class TestAuthService:
    """Тесты для AuthService"""
    
    @pytest.fixture
    def mock_user(self):
        """Мок пользователя"""
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.password_hash = PasswordManager.hash_password("test_password")
        user.full_name = "Test User"
        return user
    
    @pytest.fixture
    def mock_admin(self):
        """Мок администратора"""
        admin = MagicMock(spec=Admin)
        admin.id = 2
        admin.email = "admin@example.com"
        admin.password_hash = PasswordManager.hash_password("admin_password")
        admin.full_name = "Test Admin"
        return admin
    
    async def test_authenticate_user_success(self, mock_user):
        """Тест успешной аутентификации пользователя"""
        with patch('app.auth.service.get_db_session') as mock_get_session:
            mock_session = MagicMock(spec=AsyncSession)
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await AuthService.authenticate_user("test@example.com", "test_password")
            
            assert result == mock_user
            mock_session.execute.assert_called_once()
    
    async def test_authenticate_user_not_found(self):
        """Тест аутентификации несуществующего пользователя"""
        with patch('app.auth.service.get_db_session') as mock_get_session:
            mock_session = MagicMock(spec=AsyncSession)
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await AuthService.authenticate_user("nonexistent@example.com", "password")
            
            assert result is None
    
    async def test_authenticate_user_wrong_password(self, mock_user):
        """Тест аутентификации с неправильным паролем"""
        with patch('app.auth.service.get_db_session') as mock_get_session:
            mock_session = MagicMock(spec=AsyncSession)
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await AuthService.authenticate_user("test@example.com", "wrong_password")
            
            assert result is None
    
    async def test_authenticate_admin_success(self, mock_admin):
        """Тест успешной аутентификации администратора"""
        with patch('app.auth.service.get_db_session') as mock_get_session:
            mock_session = MagicMock(spec=AsyncSession)
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_admin
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await AuthService.authenticate_admin("admin@example.com", "admin_password")
            
            assert result == mock_admin
    
    async def test_register_user_success(self):
        """Тест успешной регистрации пользователя"""
        with patch('app.auth.service.get_db_session') as mock_get_session:
            mock_session = MagicMock(spec=AsyncSession)
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute = AsyncMock(return_value=mock_result)
            mock_session.add = MagicMock()
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            mock_user = MagicMock(spec=User)
            mock_user.email = "new@example.com"
            mock_user.full_name = "New User"
            
            with patch('app.auth.service.select') as mock_select:
                mock_select.return_value.where.return_value = MagicMock()
                
                with patch('app.auth.service.User', return_value=mock_user) as mock_user_class:
                    with patch('app.auth.service.PasswordManager.hash_password', return_value="hashed_password"):
                        result = await AuthService.register_user(
                            "new@example.com", 
                            "password123", 
                            "New User"
                        )
                        
                        assert result == mock_user
                        mock_session.add.assert_called_once_with(mock_user)
                        mock_session.commit.assert_called_once()
                        mock_session.refresh.assert_called_once_with(mock_user)
                        
                        mock_user_class.assert_called_once()
                        call_kwargs = mock_user_class.call_args[1]
                        assert call_kwargs["email"] == "new@example.com"
                        assert call_kwargs["full_name"] == "New User"
                        assert call_kwargs["password_hash"] == "hashed_password"
    
    async def test_register_user_email_exists(self):
        """Тест регистрации с уже существующим email"""
        with patch('app.auth.service.get_db_session') as mock_get_session:
            mock_session = MagicMock(spec=AsyncSession)
            
            existing_user = MagicMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = existing_user
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            with pytest.raises(ValueError, match="Пользователь с таким email уже существует"):
                await AuthService.register_user(
                    "existing@example.com", 
                    "password123", 
                    "User"
                )


class TestAuthUtilityFunctions:
    """Тесты для вспомогательных функций аутентификации"""
    
    def test_get_jwt_manager(self):
        """Тест получения JWT менеджера из запроса"""
        mock_request = MagicMock()
        mock_request.app.config.get.side_effect = lambda key, default=None: {
            "JWT_SECRET": "test_secret",
            "JWT_ALGORITHM": "HS256"
        }.get(key, default)
        
        jwt_manager = get_jwt_manager(mock_request)
        
        assert isinstance(jwt_manager, JWTManager)
        assert jwt_manager.secret_key == "test_secret"
        assert jwt_manager.algorithm == "HS256"
    
    def test_get_jwt_manager_custom_algorithm(self):
        """Тест получения JWT менеджера с кастомным алгоритмом"""
        mock_request = MagicMock()
        mock_request.app.config.get.side_effect = lambda key, default=None: {
            "JWT_SECRET": "test_secret",
            "JWT_ALGORITHM": "HS512"
        }.get(key, default)
        
        jwt_manager = get_jwt_manager(mock_request)
        assert jwt_manager.algorithm == "HS512"
    
    def test_extract_token_success(self):
        """Тест успешного извлечения токена"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Bearer test_token_123"
        
        token = extract_token(mock_request)
        assert token == "test_token_123"
    
    def test_extract_token_missing_header(self):
        """Тест извлечения токена при отсутствии заголовка"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        
        with pytest.raises(ValueError, match="Отсутствует заголовок Authorization"):
            extract_token(mock_request)
    
    def test_extract_token_invalid_format(self):
        """Тест извлечения токена с неверным форматом"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Invalid token_format"
        
        with pytest.raises(ValueError, match="Неверный формат токена"):
            extract_token(mock_request)
    
    def test_extract_token_empty_bearer(self):
        """Тест извлечения пустого Bearer токена"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Bearer "
        
        token = extract_token(mock_request)
        assert token == ""


class TestGetCurrentUser:
    """Тесты для функции get_current_user"""
    
    @pytest.fixture
    def mock_request(self):
        """Мок запроса"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Bearer test_token"
        mock_request.app.config.get.side_effect = lambda key, default=None: {
            "JWT_SECRET": "test_secret",
            "JWT_ALGORITHM": "HS256"
        }.get(key, default)
        return mock_request
    
    @pytest.fixture
    def mock_user(self):
        """Мок пользователя"""
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        return user
    
    @pytest.fixture
    def mock_admin(self):
        """Мок администратора"""
        admin = MagicMock(spec=Admin)
        admin.id = 2
        admin.email = "admin@example.com"
        return admin
    
    async def test_get_current_user_success(self, mock_request, mock_user):
        """Тест успешного получения текущего пользователя"""
        payload = {
            "user_id": 1,
            "user_type": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        
        with patch('app.auth.service.extract_token', return_value="test_token"):
            with patch('app.auth.service.get_jwt_manager') as mock_get_jwt:
                mock_jwt_manager = MagicMock()
                mock_jwt_manager.decode_token.return_value = payload
                mock_get_jwt.return_value = mock_jwt_manager
                
                with patch('app.auth.service.get_db_session') as mock_get_session:
                    mock_session = MagicMock()
                    mock_result = MagicMock()
                    mock_result.scalar_one_or_none.return_value = mock_user
                    mock_session.execute = AsyncMock(return_value=mock_result)
                    
                    mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
                    
                    result = await get_current_user(mock_request)
                    assert result == mock_user
    
    async def test_get_current_admin_success(self, mock_request, mock_admin):
        """Тест успешного получения текущего администратора"""
        payload = {
            "user_id": 2,
            "user_type": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        
        with patch('app.auth.service.extract_token', return_value="test_token"):
            with patch('app.auth.service.get_jwt_manager') as mock_get_jwt:
                mock_jwt_manager = MagicMock()
                mock_jwt_manager.decode_token.return_value = payload
                mock_get_jwt.return_value = mock_jwt_manager
                
                with patch('app.auth.service.get_db_session') as mock_get_session:
                    mock_session = MagicMock()
                    mock_result = MagicMock()
                    mock_result.scalar_one_or_none.return_value = mock_admin
                    mock_session.execute = AsyncMock(return_value=mock_result)
                    
                    mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
                    
                    result = await get_current_user(mock_request)
                    assert result == mock_admin
    
    async def test_get_current_user_invalid_token(self, mock_request):
        """Тест получения пользователя с недействительным токеном"""
        with patch('app.auth.service.extract_token', side_effect=ValueError("Invalid token")):
            with pytest.raises(ValueError, match="Ошибка аутентификации"):
                await get_current_user(mock_request)
    
    async def test_get_current_user_missing_user_id(self, mock_request):
        """Тест получения пользователя с отсутствующим user_id в токене"""
        payload = {"user_type": "user"}
        
        with patch('app.auth.service.extract_token', return_value="test_token"):
            with patch('app.auth.service.get_jwt_manager') as mock_get_jwt:
                mock_jwt_manager = MagicMock()
                mock_jwt_manager.decode_token.return_value = payload
                mock_get_jwt.return_value = mock_jwt_manager
                
                with pytest.raises(ValueError, match="Ошибка аутентификации"):
                    await get_current_user(mock_request)
    
    async def test_get_current_user_unknown_user_type(self, mock_request):
        """Тест получения пользователя с неизвестным типом"""
        payload = {
            "user_id": 1,
            "user_type": "unknown",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        
        with patch('app.auth.service.extract_token', return_value="test_token"):
            with patch('app.auth.service.get_jwt_manager') as mock_get_jwt:
                mock_jwt_manager = MagicMock()
                mock_jwt_manager.decode_token.return_value = payload
                mock_get_jwt.return_value = mock_jwt_manager
                
                with pytest.raises(ValueError, match="Ошибка аутентификации"):
                    await get_current_user(mock_request)
    
    async def test_get_current_user_not_found_in_db(self, mock_request):
        """Тест получения несуществующего пользователя"""
        payload = {
            "user_id": 999,
            "user_type": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        
        with patch('app.auth.service.extract_token', return_value="test_token"):
            with patch('app.auth.service.get_jwt_manager') as mock_get_jwt:
                mock_jwt_manager = MagicMock()
                mock_jwt_manager.decode_token.return_value = payload
                mock_get_jwt.return_value = mock_jwt_manager
                
                with patch('app.auth.service.get_db_session') as mock_get_session:
                    mock_session = MagicMock()
                    mock_result = MagicMock()
                    mock_result.scalar_one_or_none.return_value = None
                    mock_session.execute = AsyncMock(return_value=mock_result)
                    
                    mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
                    
                    with pytest.raises(ValueError, match="Ошибка аутентификации"):
                        await get_current_user(mock_request)


class TestAuthDecorators:
    """Тесты для декораторов аутентификации"""
    
    @pytest.fixture
    def mock_request(self):
        """Мок запроса"""
        mock_request = MagicMock()
        mock_request.ctx = MagicMock()
        return mock_request
    
    @pytest.fixture
    def mock_user(self):
        """Мок пользователя"""
        return MagicMock(spec=User)
    
    @pytest.fixture
    def mock_admin(self):
        """Мок администратора"""
        return MagicMock(spec=Admin)
    
    async def test_auth_required_success_with_user(self, mock_request, mock_user):
        """Тест успешной аутентификации пользователя с декоратором"""
        @auth_required()
        async def test_handler(request):
            return {"message": "success"}
        
        with patch('app.auth.service.get_current_user', return_value=mock_user):
            result = await test_handler(mock_request)
            
            assert result == {"message": "success"}
            assert mock_request.ctx.current_user == mock_user
            assert mock_request.ctx.user_type == "user"
    
    async def test_auth_required_success_with_admin(self, mock_request, mock_admin):
        """Тест успешной аутентификации администратора с декоратором"""
        @auth_required()
        async def test_handler(request):
            return {"message": "success"}
        
        with patch('app.auth.service.get_current_user', return_value=mock_admin):
            result = await test_handler(mock_request)
            
            assert result == {"message": "success"}
            assert mock_request.ctx.current_user == mock_admin
            assert mock_request.ctx.user_type == "admin"
    
    async def test_auth_required_with_specific_user_types(self, mock_request, mock_user):
        """Тест декоратора с указанными типами пользователей"""
        @auth_required(user_types=["user"])
        async def test_handler(request):
            return {"message": "success"}
        
        with patch('app.auth.service.get_current_user', return_value=mock_user):
            result = await test_handler(mock_request)
            assert result == {"message": "success"}
    
    async def test_auth_required_insufficient_permissions(self, mock_request, mock_user):
        """Тест недостаточных прав доступа"""
        @auth_required(user_types=["admin"])
        async def test_handler(request):
            return {"message": "success"}
        
        with patch('app.auth.service.get_current_user', return_value=mock_user):
            with patch('app.auth.service.sanic_json') as mock_json:
                mock_json.return_value = {"error": "Недостаточно прав доступа"}
                
                result = await test_handler(mock_request)
                
                mock_json.assert_called_once_with(
                    {"error": "Недостаточно прав доступа"}, 
                    status=403
                )
    
    async def test_auth_required_authentication_error(self, mock_request):
        """Тест ошибки аутентификации"""
        @auth_required()
        async def test_handler(request):
            return {"message": "success"}
        
        with patch('app.auth.service.get_current_user', side_effect=ValueError("Invalid token")):
            with patch('app.auth.service.sanic_json') as mock_json:
                mock_json.return_value = {"error": "Invalid token"}
                
                result = await test_handler(mock_request)
                
                mock_json.assert_called_once_with(
                    {"error": "Invalid token"}, 
                    status=401
                )
    
    async def test_auth_required_internal_error(self, mock_request):
        """Тест внутренней ошибки сервера"""
        @auth_required()
        async def test_handler(request):
            return {"message": "success"}
        
        with patch('app.auth.service.get_current_user', side_effect=Exception("Internal error")):
            with patch('app.auth.service.sanic_json') as mock_json:
                mock_json.return_value = {"error": "Внутренняя ошибка сервера"}
                
                result = await test_handler(mock_request)
                
                mock_json.assert_called_once_with(
                    {"error": "Внутренняя ошибка сервера"}, 
                    status=500
                )
    
    async def test_admin_required_success(self, mock_request, mock_admin):
        """Тест успешной авторизации администратора"""
        @admin_required
        async def test_handler(request):
            return {"message": "admin access"}
        
        with patch('app.auth.service.get_current_user', return_value=mock_admin):
            result = await test_handler(mock_request)
            assert result == {"message": "admin access"}
    
    async def test_admin_required_user_access_denied(self, mock_request, mock_user):
        """Тест отказа в доступе для обычного пользователя"""
        @admin_required
        async def test_handler(request):
            return {"message": "admin access"}
        
        with patch('app.auth.service.get_current_user', return_value=mock_user):
            with patch('app.auth.service.sanic_json') as mock_json:
                mock_json.return_value = {"error": "Недостаточно прав доступа"}
                
                result = await test_handler(mock_request)
                
                mock_json.assert_called_once_with(
                    {"error": "Недостаточно прав доступа"}, 
                    status=403
                )
    
    async def test_user_required_success(self, mock_request, mock_user):
        """Тест успешной авторизации пользователя"""
        @user_required
        async def test_handler(request):
            return {"message": "user access"}
        
        with patch('app.auth.service.get_current_user', return_value=mock_user):
            result = await test_handler(mock_request)
            assert result == {"message": "user access"}
    
    async def test_user_required_admin_access_denied(self, mock_request, mock_admin):
        """Тест отказа в доступе для администратора к пользовательским ресурсам"""
        @user_required
        async def test_handler(request):
            return {"message": "user access"}
        
        with patch('app.auth.service.get_current_user', return_value=mock_admin):
            with patch('app.auth.service.sanic_json') as mock_json:
                mock_json.return_value = {"error": "Недостаточно прав доступа"}
                
                result = await test_handler(mock_request)
                
                mock_json.assert_called_once_with(
                    {"error": "Недостаточно прав доступа"}, 
                    status=403
                )

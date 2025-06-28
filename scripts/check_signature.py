import hashlib

data = {
    'account_id': 1,
    'amount': 100,
    'transaction_id': '5eae174f-7cd0-472c-bd36-35660f00132b',
    'user_id': 1
}
secret_key = 'gfdmhghif38yrf9ew0jkf32'
signature_string = f"{data['account_id']}{data['amount']}{data['transaction_id']}{data['user_id']}{secret_key}"
print(f'String to sign: {signature_string}')
calculated_signature = hashlib.sha256(signature_string.encode()).hexdigest()
print(f'Calculated signature: {calculated_signature}')
expected = '7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8'
print(f'Expected signature: {expected}')
print(f'Match: {calculated_signature == expected}')

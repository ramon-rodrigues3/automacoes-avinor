import bitrix

card = bitrix.deal_get(11380)
estagio = card.get('STAGE_ID')
print(estagio)
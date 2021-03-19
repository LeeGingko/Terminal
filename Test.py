
s = b'U112179603321866832113243'
rxCheck = 0 # 校验和清零
dataLength = len(s)
cnt = 0
for ch in s[0:24]: # 计算校验和
    rxCheck += ch
    cnt += 1
    print(rxCheck)
print("cnt=" + str(cnt))
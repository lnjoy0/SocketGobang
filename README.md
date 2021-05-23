# SocketGobang
基于socket连接的双人五子棋游戏，使用pygame开发，分为客户端与服务端。

python与pygame版本为：
```
python 3.8.1
pygame 2.0.1
```

启动后，在客户端输入服务端的ip和端口进行连接，在双方都确认开始后，正式开始游戏。

服务端执黑棋，客户端执白棋，黑棋先行。

任意方向连成5子则获胜。

每回合落子限时30秒，共有3次超时机会，若3次机会耗尽后仍然超时，则判负。

游戏结束时，双方都按回车键可再来一局。

![image](https://user-images.githubusercontent.com/58203257/119249879-d9ffa900-bbce-11eb-9b0e-72c2cc149a1e.png)
![image](https://user-images.githubusercontent.com/58203257/119249906-16cba000-bbcf-11eb-923d-b5272a1827d0.png)
![image](https://user-images.githubusercontent.com/58203257/119249910-1df2ae00-bbcf-11eb-8a97-9a240ea8557b.png)
![image](https://user-images.githubusercontent.com/58203257/119249926-382c8c00-bbcf-11eb-9655-adaa1caa636a.png)

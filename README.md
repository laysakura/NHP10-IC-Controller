# NHP10 IC Controller

A controller of the Instrument Cluster (speedmeter) of the NHP10 (Toyota AQUA 2013).

[!['Demo movie']('https://github.com/user-attachments/assets/fd8b981c-e0e4-490e-b127-c790602d72b8')]('https://youtu.be/FkTJo1CsYN8')

## Get Started

Connect the IC to your Linux box using SocketCAN (e.g. `can0`).

```console
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0
```

Then, start the controller.

```console
python main.py can0
```

Open your browser and access `http://localhost:5000`.

## References

- [(Japanese Article) アクアのスピードメーターを解析してPS3のコントローラで動かす](https://www.shutingrz.com/post/aqua-meter-hack/)

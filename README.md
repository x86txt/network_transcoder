## JOSIE = <u>J</u>ust an <u>O</u>rdinary <u>S</u>erver for <u>I</u>nteractive <u>E</u>ncoding

### start server & client  
```python client.py```  
```python server.py```  
```python web.py```  

### submit video file  
```curl -k -F 'file=@./small.mp4' -F 'num_chunks=1' https://localhost:5000/upload```  

num_chunks = number of running clients  
gpu_or_cpu = cuda / cpu

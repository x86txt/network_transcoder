### start server & client  
```python server.py```  
```python client.py```  

### submit video file  
```curl -k -F 'file=@./small.mp4' -F 'num_chunks=1' https://localhost:5000/upload```  

num_chunks = number of running clients  
gpu_or_cpu = cuda / cpu

## Introduction
API Server and Model Serving Server for cartoon stylizer.

## Prerequisites
Code is tested on 
```
Python: 3.7.9
Pytorch: 1.6.0
Nodejs: 8.10.0
Flask: 1.1.2
```

## Model Configuration
```python
# inferece/app.py
...
config = {
    'model_path': 'your/snapshot/path.pt'  # snapshot path
}
...
```

## Running
`$ ./run.sh`

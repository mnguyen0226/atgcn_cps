# Cyber-Physical Attack Detection, Localization, & Attribution Evaluation with Temporal Graph Neural Netorks for Water Distribution Systems

Explainable TGCN for Water Distribution Systems

## Overall Pipeline
![alt-text](https://github.com/mnguyen0226/xtgcn_wds_cps/blob/main/docs/imgs/pipeline.png)

## Developing Pipeline
![alt-text](https://github.com/mnguyen0226/xtgcn_wds_cps/blob/main/docs/imgs/tgcn_train_pipeline.png)

Reference: https://github.com/lehaifeng/T-GCN/tree/master/T-GCN/T-GCN-PyTorch

python main.py --model_name TGCN --max_epochs 1 --learning_rate 0.001 --weight_decay 0 --batch_size 32 --hidden_dim 64 --loss mse_with_regularizer --settings supervised 

python main.py

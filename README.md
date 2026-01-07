## Bitcoin
This work is forked from [RajputGarima/Bitcoin](https://github.com/RajputGarima/Bitcoin). Earlier I was just using this for understanding BitCoin system as whole. But I started cleaning the code base for my own understanding. Hence following changes has been added :-
1. Refactored the full code based into simple classes, and encapsulated the operations into those classes.
2. Added few extra classes for better visibilility.
3. Every run adds the logs into `/logs/Bitcoin_<date-time>.log` files.
4. The code runs parallel threads as Nodes, but it uses `future.concurrent` library. Which inherently doesn't show any exceptions in case something's wrong. We have corrected this by adding suitable code blocks to show exception if it does fail.
5. Added logging mechanism with `__str__` implementation for each class, for easy tracking.
6. Updated variables to make logic explainable.


## ToDo
```text
1. More refactoring
2. Performed transaction still looks little off, I somehow want to show it in way where we can show a single transaction and its input and output is shown in single line.
3. Add screen shots here for better understanding
4. Add comments and understanding on the go
5. Integrate design patterns if we can...
6. Think of scalability in terms of customers of the system.
```

## Summary
Implementation of bitcoin system with 'n' number of nodes where 'n' is adjustable. There are 'n' independent threads in the system and the network between these nodes is assumed to be fully connected. A node can perform any number of transactions and the node that wins in the **proof-of-work** and satisfies **consensus requirements** finally gets to create a block which is added to the immutable block chain.

To maintain integrity of the blocks, **Merkle tree** of all the transactions present in the block is created. The tree stores hash pointers at each level. A block also stores hash pointer of the previous block in the chain. This ensures any tampering with a transaction or a block leads to disturbance in the hash values along the complete chain which can not go undetected.

Each node is given 5 wallets i.e. 5 pairs of *<publicKey, privateKey>* to give **Multi-Transaction support.** 

There is a config file *(config.py)* that allows adjusting the hyper-parameters of the Blockchain like number of nodes in the network, arity of Merkle tree, Nonce size, Hash size etc. 

For Python 3.10 :-
```bash
pip install pycryptodome
pip install prettytable
pip install crypto
pip install datetime 
```


To run the code, type
```bash
python3 main.py
```


It prints out the log of transactions starting from the initial state of each node. All the transactions along with the state of all the nodes is printed upon addition of a new block to the blockchain. <br />

The code runs infinitely as a bitcoin system is supposed to do. Random transactions would keep taking place and the nodes winning hash puzzle will keep on adding blocks to the block chain. To view the logs after addition of 1-2 blocks in the block chain, force quit the program *"Ctrl + C"* after 2 minutes of execution. 


Refer to `REPORT.pdf` for detailed implementation based analysis. 
Meanwhile one can also refer to the Bitcoin base paper. Where it all started :)



def send_transaction(chain, signed_tx):
    status, tx_hash, tx_receipt = chain.send_transaction(signed_tx)
    if not status:
        raise Exception("Transaction failed: {}".format(tx_receipt))
    else:
        return status, tx_hash, tx_receipt
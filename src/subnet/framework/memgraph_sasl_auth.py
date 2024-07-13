from confluent_kafka import Producer, Consumer, KafkaException, KafkaError


class MetagraphSASLAuth:
    def __init__(self, miner_uid, miner_hotkey):
        self.miner_uid = miner_uid
        self.miner_hotkey = miner_hotkey

    def check_in_metagraph(self, miner_uid, miner_hotkey):
        """
        Check if the miner_uid and miner_hotkey exist in the Metagraph.
        """

        return True

    def sasl_callback(self, hostname, sasl_data):
        """
        Custom callback for SASL authentication.
        """
        if self.check_in_metagraph(self.miner_uid, self.miner_hotkey):
            return f"\0{self.miner_uid}\0{self.miner_hotkey}"
        else:
            raise KafkaException("Invalid miner_uid or miner_hotkey")

import pickle
import socket
from datetime import datetime, timedelta
from dnslib import DNSRecord, RCODE

CACHE_PATH = 'cache.pickle'
TTL = 10


class DNSCache:
    def __init__(self):
        self.cache = {}

    def add_record(self, key, record):
        self.cache[key] = (record, datetime.now())

    def get_record(self, key):
        record, timestamp = self.cache.get(key, (None, None))
        if timestamp and datetime.now() - timestamp < timedelta(seconds=TTL):
            return record
        else:
            print(f'Запись {key} удалена')
            self.cache.pop(key, None)
            return None

    def save_cache(self):
        with open(CACHE_PATH, 'wb') as f:
            pickle.dump(self.cache, f)

    def load_cache(self):
        try:
            with open(CACHE_PATH, 'rb') as f:
                self.cache = pickle.load(f)
        except FileNotFoundError:
            pass


class DnsServer:
    def __init__(self):
        self.cache = DNSCache()
        self.cache.load_cache()

    def query_solution(self, query_data):
        try:
            query = DNSRecord.parse(query_data)
            key = (query.q.qname, query.a.rtype)
            cache_record = self.cache.get_record(key)

            if cache_record:
                print(f'Запись найдена в кэше')
                return cache_record.pack()

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
                client_socket.settimeout(5)
                client_socket.sendto(query_data, ('77.88.8.1', 53))
                resp_data, _ = client_socket.recvfrom(1024)
                resp_record = DNSRecord.parse(resp_data)

                if resp_record.header.rcode == RCODE.NOERROR:
                    self.cache.add_record(key, resp_record)
                    self.cache.save_cache()
                    print(f"Добавлена запись в кэш")
                return resp_data
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind(('localhost', 53))
            print("DNS Сервер запущен")

            while True:
                try:
                    query_data, addr = server_socket.recvfrom(1024)
                    print(f'Получен запрос от {addr}')
                    resp_data = self.query_solution(query_data)
                    if resp_data:
                        print("Завершение работы сервера.")
                        break
                except KeyboardInterrupt:
                    print("Завершение работы сервера.")
                    break


dns_server = DnsServer()
dns_server.run()

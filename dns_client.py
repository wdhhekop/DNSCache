import socket
from dnslib import DNSRecord, QTYPE
import random

domains = []


def query_dns(domain, query_type):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 53)

    try:
        query_data = DNSRecord.question(domain, QTYPE[query_type]).pack()
        client_socket.sendto(query_data, server_address)

        resp_data, _ = client_socket.recvfrom(1024)
        resp = DNSRecord.parse(resp_data)

        return resp
    except Exception as e:
        return f"Ошибка при выполнении DNS-запроса: {e}"
    finally:
        client_socket.close()


def main():
    for domain in domains:
        print('----------------------------')
        if '.' in domain:
            ip = socket.gethostbyname(domain)
            print(f"{domain} {ip}")
        else:
            resp = query_dns(domain, random.choice(['A', 'NS']))
            print(resp)

    print('----------------------------')


if __name__ == "__main__":
    main()

import secrets
import sys


# CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)"
CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#%^&*(-_=+)"  # retirado caractere '$'
SIZE = 50


def generate_random_string(length, charset):
    return "".join(secrets.choice(charset) for _ in range(length))


def main():
    try:
        size = int(sys.argv[1])
    except (IndexError, ValueError):
        size = SIZE

    print(generate_random_string(size, CHARSET))


if __name__ == "__main__":
    main()

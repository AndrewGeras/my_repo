def check_user_in_list(uid: int) -> bool:
    with open('users_data/users_log.txt', encoding='utf-8') as users_list:
        users = map(int, map(str.strip, users_list.readlines()))
    return uid in users


def add_user_to_list(uid: int) -> None:
    with open('users_data/users_log.txt', 'a', encoding='utf-8') as users_list:
        users_list.write(str(uid) + '\n')
import vk_api
from vk_api.keyboard import VkKeyboard

keyboard1 = vk_api.keyboard.VkKeyboard(one_time=False)
keyboard1.add_button("Назад", color=vk_api.keyboard.VkKeyboardColor.NEGATIVE)
keyboard1.add_button("Сбросить", color=vk_api.keyboard.VkKeyboardColor.SECONDARY)
keyboard1.add_button("Готово", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)

keyboard2 = vk_api.keyboard.VkKeyboard(one_time=False)
keyboard2.add_button("Назад", color=vk_api.keyboard.VkKeyboardColor.NEGATIVE)
keyboard2.add_button("Сбросить", color=vk_api.keyboard.VkKeyboardColor.SECONDARY)
keyboard2.add_button("Продолжить", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)

keyboard3 = vk_api.keyboard.VkKeyboard(one_time=False)
keyboard3.add_button("Назад", color=vk_api.keyboard.VkKeyboardColor.NEGATIVE)
keyboard3.add_button("Сбросить", color=vk_api.keyboard.VkKeyboardColor.SECONDARY)
keyboard3.add_button("Оплатил(а)", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)

keyboard4 = vk_api.keyboard.VkKeyboard(one_time=False)
keyboard4.add_button("Да", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)

keyboard5 = vk_api.keyboard.VkKeyboard(one_time=False)
keyboard5.add_button("Начать заново", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)

keyboard6 = vk_api.keyboard.VkKeyboard(one_time=False)
keyboard6.add_button("Сбросить", color=vk_api.keyboard.VkKeyboardColor.SECONDARY)

keyboard7 = vk_api.keyboard.VkKeyboard(one_time=False, inline=True)
keyboard7.add_button("Просмотр состояния принтера", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
keyboard7.add_line()
keyboard7.add_button("Остановить работу принтера", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
keyboard7.add_button("Возобновить работу принтера", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
keyboard7.add_line()
keyboard7.add_button("Пополнил бумагу(150)", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
keyboard7.add_line()
keyboard7.add_button("Пополнил тонер(2900)", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
keyboard7.add_line()
keyboard7.add_button("Печать тестовой страницы", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
keyboard7.add_line()
keyboard7.add_button("Выход", color=vk_api.keyboard.VkKeyboardColor.SECONDARY)

keyboard_location = VkKeyboard(inline=True)

keyboard_start_print = vk_api.keyboard.VkKeyboard(one_time=True)
keyboard_start_print.add_button("Печатать", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)

keyboard_pay_link = vk_api.keyboard.VkKeyboard(one_time=False, inline=True)
keyboard_pay_link.add_callback_button(label='Ссылка на оплату', color=vk_api.keyboard.VkKeyboardColor.POSITIVE, payload={"type": "open_link", "link": "https://www.hse.ru/ma/companyfin/"})
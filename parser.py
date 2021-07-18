if __name__ == '__main__':
	choice = int(input("Виберіть категорію:\n    ---> 1) Нові авто\n    ---> 2) Вживані авто\n--->  "))
	if choice == 1:
		import new_car
		new_car.main()
	elif choice == 2:
		import used_car
		used_car.main()
	else:
		quit('Не вірна категорія!\n---> Завершаю роботу... .')
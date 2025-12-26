# link('test:py/on_init', 'test', text='text')
# def a(): link('test:py/on_init', 'test', text=link('test:py/on_init', 'a'))

# for i in range(10):
#     a()
load('test:py/on_init')
print(a)

g_test(g_a)
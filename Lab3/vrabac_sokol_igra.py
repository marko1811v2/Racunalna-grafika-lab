import tkinter as tk
import os
buttons = []
base_path = ''
window = None


def onemoguci_gumbe():
    global buttons
    for button in buttons:
        button.config(state=tk.DISABLED)
    return


def omoguci_gumbe():
    global buttons
    for button in buttons:
        button.config(state=tk.NORMAL)
    return


def trigger_sokol():
    global window, base_path
    onemoguci_gumbe()
    window.update()
    with open('config.txt') as f:
        dat = f.read().splitlines()
    dat[0] = 'trigger = sokol'
    with open('config.txt', 'w') as f:
        for d in dat:
            f.write("%s\n" % d)
    omoguci_gumbe()
    window.update()
    return


def trigger_vrabac():
    global window, base_path
    onemoguci_gumbe()
    window.update()
    with open('config.txt') as f:
        dat = f.read().splitlines()
    dat[0] = 'trigger = vrabac'
    with open('config.txt', 'w') as f:
        for d in dat:
            f.write("%s\n" % d)
    omoguci_gumbe()
    window.update()
    return


def trigger_bot():
    global window, base_path
    onemoguci_gumbe()
    window.update()
    with open('config.txt') as f:
        dat = f.read().splitlines()
    dat[0] = 'trigger = bot'
    with open('config.txt', 'w') as f:
        for d in dat:
            f.write("%s\n" % d)
    omoguci_gumbe()
    window.update()
    return


def pov_vrabac():
    global window, base_path
    onemoguci_gumbe()
    window.update()
    with open('config.txt') as f:
        dat = f.read().splitlines()
    dat[1] = 'perspektiva = vrabac'
    with open('config.txt', 'w') as f:
        for d in dat:
            f.write("%s\n" % d)
    omoguci_gumbe()
    window.update()
    return


def pov_sokol():
    global window, base_path
    onemoguci_gumbe()
    window.update()
    with open('config.txt') as f:
        dat = f.read().splitlines()
    dat[1] = 'perspektiva = sokol'
    with open('config.txt', 'w') as f:
        for d in dat:
            f.write("%s\n" % d)
    omoguci_gumbe()
    window.update()
    return


def start():
    import mainigra
    return


def main():
    global buttons, base_path, window
    starter_path = (os.path.abspath(__file__))
    base_path = starter_path.split('\\')
    base_path.pop(-1)
    base_path = '\\'.join(base_path)

    with open('config.txt') as f:
        dat = f.read().splitlines()
    parametri = []
    for linija in dat:
        if linija.strip() == '' or linija[0] == '#':
            continue
        parametri.append(linija.strip().split('=')[1].strip())
    print(parametri)

    window = tk.Tk()

    b_trigger_sokol =  tk.Button(text='Trigger -> Sokol', width=20, height=5, bg='blue', fg='orange', command=trigger_sokol)
    b_trigger_vrabac = tk.Button(text='Trigger -> Vrabac', width=20, height=5, bg='blue', fg='orange', command=trigger_vrabac)
    b_trigger_bot = tk.Button(text='Trigger -> Bot', width=20, height=5, bg='blue', fg='orange', command=trigger_bot)
    b_pov_sokol = tk.Button(text='POV -> Sokol', width=20, height=5, bg='blue', fg='orange', command=pov_sokol)
    b_pov_vrabac = tk.Button(text='POV -> Vrabac', width=20, height=5, bg='blue', fg='orange', command=pov_vrabac)
    b_start = tk.Button(text='START', width=20, height=5, bg='blue', fg='orange', command=start)

    b_trigger_sokol.pack()
    b_trigger_vrabac.pack()
    b_trigger_bot.pack()
    b_pov_sokol.pack()
    b_pov_vrabac.pack()
    b_start.pack()

    buttons = [b_trigger_sokol, b_trigger_vrabac, b_trigger_bot, b_pov_sokol, b_pov_vrabac, b_start]
    window.mainloop()
    return


if __name__ == "__main__":
    main()
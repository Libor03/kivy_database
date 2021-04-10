from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, ImageLeftWidget, IconRightWidget
from kivymd.uix.menu import MDDropdownMenu
from db import Db, Person, State, City

class StateContent(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
#vytvoření nového státu
class StateDialog(MDDialog):
    def __init__(self, *args, **kwargs):
        super(StateDialog, self).__init__(
            type="custom",
            content_cls=StateContent(),
            title='Nový stát',
            size_hint=(.8, 1),
            buttons=[
                MDFlatButton(text='Uložit', on_release=self.save_dialog),
                MDFlatButton(text='Zrušit', on_release=self.cancel_dialog)
            ]
        )

    def save_dialog(self, *args):
        state = State()
        state.short_name = self.content_cls.ids.state_short_name.text
        state.full_name = self.content_cls.ids.state_full_name.text
        app.persons.database.create_state(state)
        self.dismiss()

    def cancel_dialog(self, *args):
        self.dismiss()

#vytvoření nového města
class CityContent(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

class CityDialog(MDDialog):
    def __init__(self, *args, **kwargs):
        super(CityDialog, self).__init__(
            type="custom",
            content_cls=CityContent(),
            title='Nové město',
            size_hint=(.8, 1),
            buttons=[
                MDFlatButton(text='Uložit', on_release=self.save_dialog),
                MDFlatButton(text='Zrušit', on_release=self.cancel_dialog)
            ]
        )

    def save_dialog(self, *args):
        city = City()
        city.name = self.content_cls.ids.city_name.text
        app.persons.database.create_city(city)
        self.dismiss()

    def cancel_dialog(self, *args):
        self.dismiss()

#vytvoření nové osoby - funkčnost
class PersonContent(BoxLayout):
    def __init__(self, id, *args, **kwargs):
        super().__init__(**kwargs)
        if id:
            person = vars(app.persons.database.read_by_id(id))
        else:
            person = {"id":"", "name":"jméno", "state_short": "Stát", "city":"Město"}

        self.ids.person_name.text = person['name']
        states = app.persons.database.read_states()
        #získání výpisu všech států
        menu_items = [{"viewclass": "OneLineListItem", "text": f"{state.short_name}", "on_release": lambda x=f"{state.short_name}": self.set_item(x)} for state in states]
        self.menu_states = MDDropdownMenu(
            caller=self.ids.state_item,
            items=menu_items,
            position="center",
            width_mult=5,
        )
        cities = app.persons.database.read_cities()
        #získání výpisů všech měst
        me_items = [{"viewclass": "OneLineListItem", "text": f"{city.name}",
                     "on_release": lambda x=f"{city.name}": self.sett_item(x)} for city in cities]
        self.menu_city = MDDropdownMenu(
            caller=self.ids.city_item,
            items=me_items,
            position="center",
            width_mult=5,
        )
        self.ids.city_item.set_item(person['city'])
        self.ids.city_item.text = person['city']
        self.ids.state_item.set_item(person['state_short'])
        self.ids.state_item.text = person['state_short']

    #při kliknutí se to zapíše
    def set_item(self, text_item):
        self.ids.state_item.set_item(text_item)
        self.ids.state_item.text = text_item
        self.menu_states.dismiss()

    def sett_item(self, text_item):
        self.ids.city_item.set_item(text_item)
        self.ids.city_item.text = text_item
        self.menu_city.dismiss()


#vytvoření nové osoby - menu
class PersonDialog(MDDialog):
    def __init__(self, id, *args, **kwargs):
        super(PersonDialog, self).__init__(
            type="custom",
            content_cls=PersonContent(id=id),
            title='Záznam osoby',
            text='Ahoj',
            size_hint=(.8, 1),
            buttons=[
                MDFlatButton(text='Uložit', on_release=self.save_dialog),
                MDFlatButton(text='Zrušit', on_release=self.cancel_dialog)
            ]
        )
        self.id = id

    def save_dialog(self, *args):
        person = {}
        person['name'] = self.content_cls.ids.person_name.text
        person['state_short'] = self.content_cls.ids.state_item.text
        person['city'] = self.content_cls.ids.city_item.text
        if self.id:
            person["id"] = self.id
            app.persons.update(person)
        else:
            app.persons.create(person)
        self.dismiss()

    def cancel_dialog(self, *args):
        self.dismiss()

#výpis uložených dat v databázi
class MyItem(TwoLineAvatarIconListItem):
    def __init__(self, item, *args, **kwargs):
        super(MyItem, self).__init__()
        self.id = item['id']
        self.text = item['name']
        self.secondary_text = f"{item['state_short']},  \n {item['city']}"
        self._no_ripple_effect = True
        self.image = ImageLeftWidget()
        self.image.source = f"images/{item['state_short']}.png"
        self.add_widget(self.image)
        self.icon = IconRightWidget(icon="delete", on_release=self.on_delete)
        self.add_widget(self.icon)

    #tlačítka
    def on_press(self):
        self.dialog = PersonDialog(id=self.id)
        self.dialog.open()

    def on_delete(self, *args):

        yes_button = MDFlatButton(text='Ano', on_release=self.yes_button_release)
        no_button = MDFlatButton(text='Ne', on_release=self.no_button_release)
        self.dialog_confirm = MDDialog(type="confirmation", title='Smazání záznamu', text="Chcete opravdu smazat tento záznam?", buttons=[yes_button, no_button])
        self.dialog_confirm.open()

    def yes_button_release(self, *args):
        app.persons.delete(self.id)
        self.dialog_confirm.dismiss()

    def no_button_release(self, *args):
        self.dialog_confirm.dismiss()

#celá stránka, funkční i grafická část
class Persons(BoxLayout):
    # Metoda konstruktoru
    def __init__(self, *args, **kwargs):
        super(Persons, self).__init__(orientation="vertical")
        global app
        app = App.get_running_app()
        scrollview = ScrollView()
        self.list = MDList()
        self.database = Db(dbtype='sqlite', dbname='persons.db')
        self.rewrite_list()
        scrollview.add_widget(self.list)
        self.add_widget(scrollview)
        button_box = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        new_person_btn = MDFillRoundFlatIconButton()
        new_person_btn.text = "Nová osoba"
        new_person_btn.icon = "plus"
        new_person_btn.icon_color = [0.9, 0.9, 0.9, 1]
        new_person_btn.text_color = [0.9, 0.9, 0.9, 1]
        new_person_btn.md_bg_color = [0, 0.5, 0.8, 1]
        new_person_btn.font_style = "Button"
        new_person_btn.pos_hint = {"center_x": .5}
        new_person_btn.on_release = self.on_create_person
        button_box.add_widget(new_person_btn)

        new_state_btn = MDFillRoundFlatIconButton()
        new_state_btn.text = "Nový stát"
        new_state_btn.icon = "plus"
        new_state_btn.icon_color = [0.9, 0.9, 0.9, 1]
        new_state_btn.text_color = [0.9, 0.9, 0.9, 1]
        new_state_btn.md_bg_color = [0.8, 0.5, 0, 1]
        new_state_btn.font_style = "Button"
        new_state_btn.pos_hint = {"center_x": .6}
        new_state_btn.on_release = self.on_create_state
        button_box.add_widget(new_state_btn)

        new_city_btn = MDFillRoundFlatIconButton()
        new_city_btn.text = "Nové město"
        new_city_btn.icon = "plus"
        new_city_btn.icon_color = [0.9, 0.9, 0.9, 1]
        new_city_btn.text_color = [0.9, 0.9, 0.9, 1]
        new_city_btn.md_bg_color = [0.8, 0.5, 0.5, 1]
        new_city_btn.font_style = "Button"
        new_city_btn.pos_hint = {"center_x": 1}
        new_city_btn.on_release = self.on_create_city
        button_box.add_widget(new_city_btn)
        self.add_widget(button_box)

    #funkce
    def rewrite_list(self):
        self.list.clear_widgets()
        persons = self.database.read_all()
        for person in persons:
            print(vars(person))
            self.list.add_widget(MyItem(item=vars(person)))

    def on_create_person(self, *args):
        self.dialog = PersonDialog(id=None)
        self.dialog.open()

    def on_create_state(self, *args):
        self.dialog = StateDialog()
        self.dialog.open()

    def on_create_city(self, *args):
        self.dialog = CityDialog()
        self.dialog.open()
    def create(self, person):
        create_person = Person()
        create_person.name = person['name']
        create_person.state_short = person['state_short']
        create_person.city = person['city']
        self.database.create(create_person)
        self.rewrite_list()

    def create_test_data(self):

        create_person = Person()
        create_person.name = "testovací jméno"
        create_person.state_short = "testovací stát"
        create_person.city = "testovací město"
        self.database.create(create_person)
        self.rewrite_list()

    def update(self, person):

        update_person = self.database.read_by_id(person['id'])
        update_person.name = person['name']
        update_person.state_short = person['state_short']
        self.database.update()
        self.rewrite_list()

    def delete(self, id):

        self.database.delete(id)
        self.rewrite_list()
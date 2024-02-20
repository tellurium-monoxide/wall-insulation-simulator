class Localizer:

    def __init__(self):
        self.langs=[]
        self.lang=""
        self.texts={}
        self.links={}
        self.missing={}


    def get_text(self, text_id):
        if text_id in self.texts[self.lang]:
            return self.texts[self.lang][text_id]
        else:
            self.missing[self.lang][text_id]="missing"
            return "missing text"


    def set_text(self, lang, text_id, text):
        self.texts[lang][text_id]=text
        try:
            self.missing[lang].pop(text_id)
        except ValueError:
            return

    def link(self,setter, text_id, link_name, text="missing text"):
        if self.get_text(text_id)=="missing text":
            self.set_text(self.lang, text_id, text)

        setter(self.get_text(text_id))
        self.links[link_name]=(setter,text_id)


    def add_lang(self, lang):
        self.langs.append(lang)
        self.texts[lang]={}
        self.missing[lang]={}
        self.lang=self.langs[0]

    def set_lang(self, lang):
        if lang in self.langs:
            self.lang=lang
            keys_to_del=[]
            for key, link in self.links.items():
                setter,text_id=link
                try:
                    setter(self.get_text(text_id))
                except RuntimeError:
                    keys_to_del.append(key)

                    continue
            for key in keys_to_del:
                self.links.pop(key)
            return True
        else:
            return False

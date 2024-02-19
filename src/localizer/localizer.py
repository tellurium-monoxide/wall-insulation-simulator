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
    def link(self,setter, text_id, link_name):

        setter(self.get_text(text_id))
        self.links[link_name]=(setter,text_id)


    def add_lang(self, lang):
        self.langs.append(lang)
        self.texts[lang]={}
        self.missing[lang]={}
        self.lang=self.langs[0]

    def set_lang(self, lang):
        self.lang=lang
        for key, link in self.links.items():
            setter,text_id=link
            try:
                setter(self.get_text(text_id))
            except RuntimeError:
                self.links.pop(key)
                continue


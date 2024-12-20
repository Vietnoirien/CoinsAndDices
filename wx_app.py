import wx
import wx.grid
import random
import json
import os
import re

class CustomDiceDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Créer un dé personnalisé", size=(400, 600))
        
        # Configuration de la fenêtre principale
        self.SetMinSize((400, 400))
        self.SetMaxSize((600, 800))
        
        # Stockage persistant des valeurs
        self.stored_values = []
        
        # Création du sizer principal
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Configuration du ScrolledWindow
        self.scroll_panel = wx.ScrolledWindow(self)
        self.scroll_panel.SetScrollRate(0, 20)
        
        # Création du panel principal
        self.panel = wx.Panel(self.scroll_panel)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Création des contrôles pour le nom
        name_sizer = self.create_name_controls()
        panel_sizer.Add(name_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Création des contrôles pour le nombre de faces
        faces_sizer = self.create_faces_controls()
        panel_sizer.Add(faces_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Initialisation du conteneur pour les valeurs des faces
        self.values_ctrls = []
        self.values_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer.Add(self.values_sizer, 1, wx.EXPAND|wx.ALL, 5)
        
        # Ajout des boutons
        btn_sizer = self.create_buttons()
        panel_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        # Configuration finale des sizers
        self.panel.SetSizer(panel_sizer)
        self.scroll_panel.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.scroll_panel.GetSizer().Add(self.panel, 1, wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(self.scroll_panel, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        
        # Initialisation des faces
        self.update_faces_inputs(6)
        
        self.Fit()
        
    def create_name_controls(self):
        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_label = wx.StaticText(self.panel, label="Nom du dé:")
        self.name_ctrl = wx.TextCtrl(self.panel)
        name_sizer.Add(name_label, 0, wx.ALL|wx.CENTER, 5)
        name_sizer.Add(self.name_ctrl, 1, wx.ALL|wx.EXPAND, 5)
        return name_sizer
        
    def create_faces_controls(self):
        faces_sizer = wx.BoxSizer(wx.HORIZONTAL)
        faces_label = wx.StaticText(self.panel, label="Nombre de faces:")
        self.faces_ctrl = wx.SpinCtrl(self.panel, min=2, max=100, initial=6)
        self.faces_ctrl.Bind(wx.EVT_SPINCTRL, self.on_faces_changed)
        faces_sizer.Add(faces_label, 0, wx.ALL|wx.CENTER, 5)
        faces_sizer.Add(self.faces_ctrl, 1, wx.ALL|wx.EXPAND, 5)
        return faces_sizer
        
    def create_buttons(self):
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self.panel, wx.ID_OK, "Créer")
        cancel_btn = wx.Button(self.panel, wx.ID_CANCEL, "Annuler")
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        return btn_sizer
        
    def update_faces_inputs(self, num_faces):
        # Sauvegarder toutes les valeurs actuelles
        current_values = [ctrl.GetValue() for ctrl in self.values_ctrls]
        
        # Mettre à jour le stockage persistant
        if len(current_values) > len(self.stored_values):
            self.stored_values.extend(current_values[len(self.stored_values):])
        else:
            for i, value in enumerate(current_values):
                if i < len(self.stored_values):
                    self.stored_values[i] = value
        
        # Nettoyer les contrôles existants
        self.cleanup()
        
        # Créer les nouveaux contrôles
        for i in range(num_faces):
            face_sizer = wx.BoxSizer(wx.HORIZONTAL)
            face_label = wx.StaticText(self.panel, label=f"Face {i+1}:")
            ctrl = wx.TextCtrl(self.panel)
            
            # Restaurer la valeur depuis le stockage persistant
            if i < len(self.stored_values):
                ctrl.SetValue(self.stored_values[i])
                
            self.values_ctrls.append(ctrl)
            face_sizer.Add(face_label, 0, wx.ALL|wx.CENTER, 5)
            face_sizer.Add(ctrl, 1, wx.ALL|wx.EXPAND, 5)
            self.values_sizer.Add(face_sizer, 0, wx.EXPAND)
        
        self.panel.Layout()
        self.scroll_panel.FitInside()
        
    def on_faces_changed(self, event):
        self.update_faces_inputs(self.faces_ctrl.GetValue())
        
    def validate_inputs(self):
        if not self.name_ctrl.GetValue().strip():
            wx.MessageBox("Le nom du dé ne peut pas être vide", "Erreur", wx.OK | wx.ICON_ERROR)
            return False
        
        for i, ctrl in enumerate(self.values_ctrls):
            if not ctrl.GetValue().strip():
                wx.MessageBox(f"La face {i+1} ne peut pas être vide", "Erreur", wx.OK | wx.ICON_ERROR)
                return False
        return True
        
    def cleanup(self):
        for ctrl in self.values_ctrls:
            ctrl.Destroy()
        self.values_ctrls.clear()
        self.values_sizer.Clear(True)
        
    def on_ok(self, event):
        if self.validate_inputs():
            event.Skip()
            
    def get_values(self):
        return {
            'name': self.name_ctrl.GetValue().strip(),
            'faces': [ctrl.GetValue().strip() for ctrl in self.values_ctrls]
        }

class CoinFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Lanceur de Pièces', size=(800, 600))
        self.panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Section contrôles
        coin_ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.coin_input = wx.SpinCtrl(self.panel, min=1, max=100, initial=1)
        coin_ctrl_sizer.Add(wx.StaticText(self.panel, label="Nombre de pièces:"), 0, wx.ALL|wx.CENTER, 5)
        coin_ctrl_sizer.Add(self.coin_input, 1, wx.ALL, 5)
        sizer.Add(coin_ctrl_sizer, 0, wx.EXPAND)
        
        # Bouton de lancement
        flip_btn = wx.Button(self.panel, label="Lancer les pièces")
        flip_btn.Bind(wx.EVT_BUTTON, self.on_flip_coins)
        sizer.Add(flip_btn, 0, wx.ALL, 5)
        
        # Grille de résultats avec séquence
        self.grid = wx.grid.Grid(self.panel)
        self.grid.CreateGrid(3, 2)
        self.grid.SetColLabelValue(0, "Résultat")
        self.grid.SetColLabelValue(1, "Détails")
        
        # Configuration de l'alignement et du retour à la ligne
        attr = wx.grid.GridCellAttr()
        attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        self.grid.SetColAttr(1, attr)
        
        self.grid.AutoSizeColumns()
        sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panel.SetSizer(sizer)
        self.Center()
        self.Show()

    def format_sequence(self, results, items_per_line=15):
        formatted_lines = []
        for i in range(0, len(results), items_per_line):
            line_items = results[i:i + items_per_line]
            formatted_lines.append(" → ".join(line_items))
        return "\n".join(formatted_lines)

    def on_flip_coins(self, event):
        num_coins = self.coin_input.GetValue()
        results = ['Pile' if random.random() < 0.5 else 'Face' for _ in range(num_coins)]
        
        self.grid.ClearGrid()
        
        piles = results.count('Pile')
        faces = results.count('Face')
        
        self.grid.SetCellValue(0, 0, "Pile")
        self.grid.SetCellValue(0, 1, str(piles))
        self.grid.SetCellValue(1, 0, "Face")
        self.grid.SetCellValue(1, 1, str(faces))
        self.grid.SetCellValue(2, 0, "Séquence")
        self.grid.SetCellValue(2, 1, self.format_sequence(results))
        
        # Ajustement automatique des dimensions
        self.grid.AutoSizeColumns()
        self.grid.AutoSizeRow(2)

class CustomDiceFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Dés Personnalisés', size=(800, 600))
        self.panel = wx.Panel(self)
        self.custom_dices = self.load_custom_dices()
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Section création nouveau dé
        new_dice_btn = wx.Button(self.panel, label="Créer un nouveau dé")
        new_dice_btn.Bind(wx.EVT_BUTTON, self.on_new_custom_dice)
        main_sizer.Add(new_dice_btn, 0, wx.ALL|wx.CENTER, 5)

        # Section contrôles des dés
        dice_ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.custom_dice_choice = wx.Choice(self.panel, choices=list(self.custom_dices.keys()))
        self.custom_dice_number = wx.SpinCtrl(self.panel, min=1, max=100, initial=1)
        
        dice_ctrl_sizer.Add(wx.StaticText(self.panel, label="Sélectionner le dé:"), 0, wx.ALL|wx.CENTER, 5)
        dice_ctrl_sizer.Add(self.custom_dice_choice, 1, wx.ALL, 5)
        dice_ctrl_sizer.Add(wx.StaticText(self.panel, label="Nombre:"), 0, wx.ALL|wx.CENTER, 5)
        dice_ctrl_sizer.Add(self.custom_dice_number, 0, wx.ALL, 5)

        # Boutons d'édition et de suppression
        edit_btn = wx.Button(self.panel, label="Éditer")
        delete_btn = wx.Button(self.panel, label="Supprimer")
        edit_btn.Bind(wx.EVT_BUTTON, self.on_edit_custom_dice)
        delete_btn.Bind(wx.EVT_BUTTON, self.on_delete_custom_dice)
        
        dice_ctrl_sizer.Add(edit_btn, 0, wx.ALL, 5)
        dice_ctrl_sizer.Add(delete_btn, 0, wx.ALL, 5)
        
        main_sizer.Add(dice_ctrl_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Bouton de lancement
        roll_btn = wx.Button(self.panel, label="Lancer")
        roll_btn.Bind(wx.EVT_BUTTON, self.on_roll_custom_dice)
        main_sizer.Add(roll_btn, 0, wx.ALL|wx.CENTER, 5)
        
        # Zone de résultats
        self.custom_result = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(700, 400))
        main_sizer.Add(self.custom_result, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Show()

    def on_new_custom_dice(self, event):
        dialog = CustomDiceDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            dice_data = dialog.get_values()
            self.save_custom_dice(dice_data['name'], dice_data['faces'])
            self.custom_dice_choice.SetItems(list(self.custom_dices.keys()))
            self.custom_dice_choice.SetStringSelection(dice_data['name'])
        dialog.Destroy()

    def on_edit_custom_dice(self, event):
        if self.custom_dice_choice.GetSelection() == -1:
            return
            
        dice_name = self.custom_dice_choice.GetString(self.custom_dice_choice.GetSelection())
        dice_data = self.custom_dices[dice_name]
        
        dialog = CustomDiceDialog(self)
        dialog.name_ctrl.SetValue(dice_name)
        dialog.faces_ctrl.SetValue(dice_data['faces'])
        
        for i, value in enumerate(dice_data['values']):
            dialog.values_ctrls[i].SetValue(value)
        
        if dialog.ShowModal() == wx.ID_OK:
            new_data = dialog.get_values()
            del self.custom_dices[dice_name]
            self.save_custom_dice(new_data['name'], new_data['faces'])
            self.custom_dice_choice.SetItems(list(self.custom_dices.keys()))
            self.custom_dice_choice.SetStringSelection(new_data['name'])
        
        dialog.Destroy()

    def on_delete_custom_dice(self, event):
        if self.custom_dice_choice.GetSelection() == -1:
            return
            
        dice_name = self.custom_dice_choice.GetString(self.custom_dice_choice.GetSelection())
        dlg = wx.MessageDialog(self,
            f"Êtes-vous sûr de vouloir supprimer le dé '{dice_name}' ?",
            "Confirmation de suppression",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        
        if dlg.ShowModal() == wx.ID_YES:
            del self.custom_dices[dice_name]
            self.save_custom_dices()
            self.custom_dice_choice.SetItems(list(self.custom_dices.keys()))
            self.custom_result.SetValue("")

    def load_custom_dices(self):
        try:
            if os.path.exists('custom_dices.json'):
                with open('custom_dices.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except json.JSONDecodeError:
            return {}

    def save_custom_dice(self, name, values):
        self.custom_dices[name] = {
            'faces': len(values),
            'values': values
        }
        self.save_custom_dices()

    def save_custom_dices(self):
        with open('custom_dices.json', 'w', encoding='utf-8') as f:
            json.dump(self.custom_dices, f, ensure_ascii=False, indent=2)

    def on_roll_custom_dice(self, event):
        if self.custom_dice_choice.GetSelection() == -1:
            return
        
        dice_name = self.custom_dice_choice.GetString(self.custom_dice_choice.GetSelection())
        number = self.custom_dice_number.GetValue()
        results = self.roll_custom_dice(dice_name, number)
        self.custom_result.SetValue("\n".join(map(str, results)))

    def roll_custom_dice(self, dice_name, number):
        if dice_name in self.custom_dices:
            return [random.choice(self.custom_dices[dice_name]['values']) for _ in range(number)]
        return []

class HomePage(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Lanceur de Dés - Menu Principal', size=(1024, 768))
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Titre principal
        title = wx.StaticText(self.panel, label="Bienvenue dans le Lanceur de Dés")
        title.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(title, 0, wx.ALL|wx.CENTER, 20)
        
        # Définition des boutons et leurs actions
        buttons_data = [
            ("Dés Standards", "Lancez des dés classiques avec notation NdX", self.open_dice_frame),
            ("Pièces", "Simulez des lancers de pièces", self.open_coins),
            ("Dés Personnalisés", "Créez et utilisez vos propres dés", self.open_custom_dice),
            ("Dés Runebound", "Dés spéciaux pour Runebound", self.open_runebound)
        ]
        
        # Création des boutons avec leurs descriptions
        for label, description, handler in buttons_data:
            button_panel = wx.Panel(self.panel)
            button_sizer = wx.BoxSizer(wx.VERTICAL)
            
            btn = wx.Button(button_panel, label=label, size=(300, 60))
            btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            btn.Bind(wx.EVT_BUTTON, handler)
            
            desc = wx.StaticText(button_panel, label=description)
            desc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
            
            button_sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
            button_sizer.Add(desc, 0, wx.ALL|wx.CENTER, 5)
            
            button_panel.SetSizer(button_sizer)
            main_sizer.Add(button_panel, 0, wx.ALL|wx.CENTER, 10)
        
        # Bouton Quitter
        quit_btn = wx.Button(self.panel, label="Quitter", size=(200, 40))
        quit_btn.Bind(wx.EVT_BUTTON, self.on_quit)
        main_sizer.Add(quit_btn, 0, wx.ALL|wx.CENTER, 20)
        
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Show()

    def open_dice_frame(self, event):
        self.Hide()
        frame = StandardDiceFrame()
        frame.Bind(wx.EVT_CLOSE, lambda evt: self.on_child_close(evt, frame))

    def open_coins(self, event):
        self.Hide()
        frame = CoinFrame()
        frame.Bind(wx.EVT_CLOSE, lambda evt: self.on_child_close(evt, frame))

    def open_custom_dice(self, event):
        self.Hide()
        frame = CustomDiceFrame()
        frame.Bind(wx.EVT_CLOSE, lambda evt: self.on_child_close(evt, frame))

    def open_runebound(self, event):
        self.Hide()
        frame = RuneboundFrame()
        frame.Bind(wx.EVT_CLOSE, lambda evt: self.on_child_close(evt, frame))

    def on_child_close(self, event, frame):
        frame.Destroy()
        self.Show()
        event.Skip()

    def on_quit(self, event):
        self.Close()

class StandardDiceFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Lanceur de Dés Standards', size=(800, 600))
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Zone de saisie
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dice_input = wx.TextCtrl(self.panel, size=(300, -1))
        input_sizer.Add(wx.StaticText(self.panel, label="Notation (ex: 2d6 3d8):"), 0, wx.ALL|wx.CENTER, 5)
        input_sizer.Add(self.dice_input, 1, wx.ALL, 5)
        main_sizer.Add(input_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Bouton de lancement
        roll_btn = wx.Button(self.panel, label="Lancer les dés")
        roll_btn.Bind(wx.EVT_BUTTON, self.on_roll_dice)
        main_sizer.Add(roll_btn, 0, wx.ALL|wx.CENTER, 5)
        
        # Grille de résultats
        self.grid = wx.grid.Grid(self.panel)
        self.grid.CreateGrid(0, 5)
        self.grid.SetColLabelValue(0, "Notation")
        self.grid.SetColLabelValue(1, "Détails des lancers")
        self.grid.SetColLabelValue(2, "Total")
        self.grid.SetColLabelValue(3, "Moyenne")
        self.grid.SetColLabelValue(4, "Min/Max")
        self.grid.AutoSizeColumns()
        main_sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)

        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Show()

    def format_rolls_display(self, rolls, max_per_line=30):
        """
        Formate les résultats des dés sur plusieurs lignes
        pour une meilleure lisibilité
        """
        formatted_lines = []
        for i in range(0, len(rolls), max_per_line):
            chunk = rolls[i:i + max_per_line]
            formatted_lines.append(str(chunk))
        return '\n'.join(formatted_lines)

    def parse_dice_notation(self, notation):
        """
        Parse une notation de dés de type XdY où:
        X = nombre de dés
        Y = nombre de faces
        """
        match = re.match(r'(\d+)d(\d+)', notation.lower())
        if match:
            return int(match.group(1)), int(match.group(2))
        return None

    def roll_dice(self, number, sides):
        """
        Lance le nombre spécifié de dés avec le nombre de faces donné
        """
        return [random.randint(1, sides) for _ in range(number)]

    def on_roll_dice(self, event):
        dice_notations = self.dice_input.GetValue().split()
        
        self.grid.ClearGrid()
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        self.grid.AppendRows(len(dice_notations))
        
        for i, notation in enumerate(dice_notations):
            parsed = self.parse_dice_notation(notation)
            if parsed:
                num_dice, sides = parsed
                rolls = self.roll_dice(num_dice, sides)
                total = sum(rolls)
                average = total / len(rolls)
                
                formatted_rolls = self.format_rolls_display(rolls)
                
                self.grid.SetCellValue(i, 0, notation)
                self.grid.SetCellValue(i, 1, formatted_rolls)
                self.grid.SetCellValue(i, 2, str(total))
                self.grid.SetCellValue(i, 3, f"{average:.2f}")
                self.grid.SetCellValue(i, 4, f"Min: {min(rolls)} | Max: {max(rolls)}")
                
                # Configuration de l'affichage de la cellule
                self.grid.SetCellSize(i, 1, 1, 1)
                attr = wx.grid.GridCellAttr()
                attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
                attr.SetReadOnly(True)
                self.grid.SetRowAttr(i, attr)
        
        self.grid.AutoSizeRows()
        self.grid.AutoSizeColumns()
        
class RuneboundFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Dés Runebound', size=(800, 600))
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.faces = [
            ["Marais", "Riviere"],
            ["Montagne", "Plaine", "Route"],
            ["Riviere", "Foret"],
            ["Route", "Plaine", "Colline"],
            ["Route", "Riviere"],
            ["Route", "Plaine", "Colline"]
        ]
        
        self.dice_count = wx.SpinCtrl(self.panel, min=1, max=10, initial=1)
        dice_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dice_sizer.Add(wx.StaticText(self.panel, label="Nombre de dés:"), 0, wx.ALL|wx.CENTER, 5)
        dice_sizer.Add(self.dice_count, 0, wx.ALL, 5)
        main_sizer.Add(dice_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        roll_btn = wx.Button(self.panel, label="Lancer les dés")
        roll_btn.Bind(wx.EVT_BUTTON, self.on_roll_dice)
        main_sizer.Add(roll_btn, 0, wx.ALL|wx.CENTER, 5)
        
        self.result_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(700, 400))
        main_sizer.Add(self.result_text, 1, wx.EXPAND|wx.ALL, 5)
        
        self.panel.SetSizer(main_sizer)
        self.Center()
        self.Show()

    def on_roll_dice(self, event):
        num_dice = self.dice_count.GetValue()
        results = []
        
        for i in range(num_dice):
            face = random.choice(self.faces)
            results.append(f"Dé {i+1}: {', '.join(face)}")
        
        self.result_text.SetValue("\n".join(results))

def main():
    app = wx.App()
    home = HomePage()
    app.MainLoop()

if __name__ == '__main__':
    main()

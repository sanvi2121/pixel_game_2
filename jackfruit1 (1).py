import wx
import os
import random
from PIL import Image

# Pixelation function
def pixelate(image, pixel_size):
    small = image.resize((max(1, image.width // pixel_size), max(1, image.height // pixel_size)),Image.NEAREST)
    return small.resize(image.size, Image.NEAREST)

# Main Game Window
class Game(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Guess the Image", size=(600, 700))

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.theme = os.path.join(BASE_DIR, "images")

        self.images = [img for img in os.listdir(self.theme) if img.lower().endswith((".png", ".jpg", ".jpeg"))]

        self.rounds = 5
        self.score = 0

        # Hard → Medium → Easy (pixel_size, penalty)
        self.guess_levels = [("Hard", 20, 1), ("Medium",10, 2), ("Easy",5, 3)]

        # UI
        panel = wx.Panel(self)

        self.info = wx.StaticText(panel, label="", pos=(20, 20))
        self.image_box = wx.StaticBitmap(panel, pos=(75, 60), size=(450, 450))
        self.input_box = wx.TextCtrl(panel, pos=(150, 540), size=(300, 30))
        self.submit_btn = wx.Button(panel, label="Submit", pos=(250, 580))
        self.submit_btn.Bind(wx.EVT_BUTTON, self.check_guess)

        self.result = wx.StaticText(panel, label="", pos=(20, 630))
        self.restart_btn = wx.Button(panel, label="Restart Game", pos=(230, 660))
        self.restart_btn.Bind(wx.EVT_BUTTON, self.restart_game)
        self.restart_btn.Hide()

        self.start_game()
        self.Show()
    
    # Game start
    def start_game(self):
        self.current_round = 1
        self.score = 0
        self.used_images = []
        self.restart_btn.Hide()
        self.submit_btn.Enable()
        self.start_round()

    # Start one round
    def start_round(self):
        if self.current_round > self.rounds:
            self.info.SetLabel(f"GAME OVER! Final score: {self.score}")
            self.info.SetFont(wx.Font(25, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Comic Sans MS"))
            self.result.SetLabel("")
            self.submit_btn.Disable()
            self.restart_btn.Show()
            return

        self.guess_index = 0
        self.wrong_penalty = 0

        available_images = list(set(self.images) - set(self.used_images))
        img_file = random.choice(available_images)
        self.used_images.append(img_file)
        self.correct_answer = os.path.splitext(img_file)[0].lower()
        path = os.path.join(self.theme, img_file)
        self.original_img = Image.open(path)

        self.show_pixelated()

    # Show pixelated image level
    def show_pixelated(self):
        level_name, pixel_size, _ = self.guess_levels[self.guess_index]
        self.info.SetLabel(f"Round {self.current_round}/{self.rounds} | Difficulty: {level_name}")

        px = pixelate(self.original_img, pixel_size)
        px = px.resize((450, 450))
        wx_img = wx.Bitmap.FromBufferRGBA(px.width, px.height, px.convert("RGBA").tobytes())
        self.image_box.SetBitmap(wx_img)

        # Clear and focus the textbox
        self.input_box.SetValue("")
        self.input_box.SetFocus()
        self.input_box.Refresh()

    # Check Guess
    def check_guess(self, event):
        guess = self.input_box.GetValue().strip().lower()

        if guess == self.correct_answer:
            self.score += 10
            self.result.SetLabel(f"Correct! Score: {self.score}")
            self.current_round += 1
            wx.CallLater(1000, self.start_round)
            return

        # Wrong guess
        if self.guess_index < len(self.guess_levels):
            _, _, penalty = self.guess_levels[self.guess_index]
            self.wrong_penalty += penalty
        self.guess_index += 1

        if self.guess_index < len(self.guess_levels):
            self.show_pixelated()  # updates image and clears textbox

            tries_left = len(self.guess_levels) - self.guess_index
            if tries_left == 2:
                msg = "Wrong! You have 2 more tries."
            elif tries_left == 1:
                msg = "Wrong! You have 1 more try."
            else:
                msg = "Last try!"

            self.result.SetLabel(msg)

        else:
            # All wrong
            self.score -= self.wrong_penalty
            self.result.SetLabel(f"All wrong! -{self.wrong_penalty} points")

            # show full image
            full = self.original_img.resize((450, 450))
            wx_img = wx.Bitmap.FromBufferRGBA(full.width, full.height, full.convert("RGBA").tobytes())
            self.image_box.SetBitmap(wx_img)

            self.current_round += 1
            wx.CallLater(1500, self.start_round)

    # Restart Game
    def restart_game(self, event):
        self.start_game()

# Run the App
app = wx.App()
Game()
app.MainLoop()
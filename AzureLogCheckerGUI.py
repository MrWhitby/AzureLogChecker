import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pycountry


class SignInLogAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Azure Log Analyzer")
        self.root.geometry("600x400")  # Expanded window size

        # Initialize variables
        self.filename = None
        self.data = None

        # Set up GUI components
        Label(self.root, text="Select Log File:").grid(row=0, column=0, pady=5, sticky=W)
        Button(self.root, text="Open Log File", command=self.load_file).grid(row=0, column=1, pady=5, sticky=W)

        # Country selection dropdown with keyboard search functionality
        Label(self.root, text="Select Country:").grid(row=1, column=0, pady=5, sticky=W)
        self.country_dropdown = CountrySearchDropdown(self.root)
        self.country_dropdown.grid(row=1, column=1, pady=5, sticky=W)
        self.country_dropdown.set("United Kingdom")  # Set a default value

        Button(self.root, text="Analyze", command=self.analyze_logs).grid(row=2, column=0, columnspan=2, pady=10)

        self.result_label = Label(self.root, text="")
        self.result_label.grid(row=3, column=0, columnspan=2, pady=10)

        # Scrolling Text Widget for detailed output
        self.details_text = scrolledtext.ScrolledText(self.root, wrap=WORD, height=10, width=70)
        self.details_text.grid(row=4, column=0, columnspan=2, pady=10)
        self.details_text.config(state=DISABLED)  # Disable editing of the text widget

        # Read Me Button
        Button(self.root, text="Read Me", command=self.open_readme).grid(row=5, column=1, pady=5, sticky=E)

    def load_file(self):
        self.filename = filedialog.askopenfilename(title="Select file", filetypes=(("CSV files", "*.csv"),))
        if self.filename:
            try:
                self.data = pd.read_csv(self.filename, low_memory=False)
                messagebox.showinfo("File Loaded", "Log file successfully loaded.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")

    def analyze_logs(self):
        selected_country = self.country_dropdown.get()
        if self.data is not None and selected_country and selected_country != '------------':
            try:
                selected_country_code = pycountry.countries.lookup(selected_country).alpha_2
                if 'Location' in self.data.columns:
                    regex_pattern = fr",\s*{selected_country_code}$"
                    mask = ~self.data['Location'].str.contains(regex_pattern, case=False, na=False, regex=True)

                    non_matching_locations = self.data.loc[mask, 'Location']
                    non_matching_indices = list(self.data.loc[mask].index)

                    count = non_matching_locations.shape[0]
                    self.result_label.config(text=f"Sign-ins from outside {selected_country_code}: {count}")
                    self.display_details(non_matching_indices, non_matching_locations)
                else:
                    messagebox.showerror("Error", "'Location' column not found in the CSV.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            messagebox.showerror("Error", "Please load a CSV file and select a valid country.")

    def display_details(self, indices, locations):
        self.details_text.config(state=NORMAL)  # Enable editing to update text
        self.details_text.delete(1.0, END)  # Clear previous content
        for index, location in zip(indices, locations):
            self.details_text.insert(END, f"Row {index}: {location}\n")
        self.details_text.config(state=DISABLED)  # Disable editing after update

    def open_readme(self):
        # Create a top-level window for the Read Me content
        readme_window = Toplevel(self.root)
        readme_window.title("Read Me")
        readme_window.geometry("600x300")
        readme_text = scrolledtext.ScrolledText(readme_window, wrap=WORD, height=15, width=70)
        readme_text.pack(pady=10)
        readme_text.insert(END,
                           "1. Import your Azure Sign-in Logs - The exported logs should be only successful sign-ins and no other filters from default.\n"
                           "2. Select the country of your country's primary source of business.\n"
                           "   2a. If your business is located in the United Kingdom so sign-ins from outside the United Kingdom may be of concern, you would select United Kingdom.\n"
                           "3. The program will provide you with a list of lines within the file that do not match the country you select along with the country on that line.")
        readme_text.config(state=DISABLED)  # Disable editing of the text widget


class CountrySearchDropdown(ttk.Combobox):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        # List specific countries at the top followed by the rest
        top_countries = ['United Kingdom', 'United States', 'Canada', 'United Arab Emirates']
        rest_of_countries = [country.name for country in pycountry.countries if country.name not in top_countries]
        self.countries = top_countries + ['------------'] + rest_of_countries
        self.filtered_countries = self.countries[:]
        self['values'] = self.filtered_countries
        self.bind('<Key>', self.search_country)

    def search_country(self, event):
        search_term = event.char
        self.filtered_countries = [country for country in self.countries if search_term.lower() in country.lower()]
        self['values'] = self.filtered_countries


def main():
    root = tk.Tk()
    app = SignInLogAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()

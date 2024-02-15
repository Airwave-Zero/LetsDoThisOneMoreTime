using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;

namespace scheduler_test1
{
    public partial class ShiftForm : Form
    {
        public string shiftFileName;
        public string shiftFileRaw;
        public ShiftForm(string fileName = "")
        {
            shiftFileName = fileName;
            InitializeComponent();
        }

        private void panel1_Paint(object sender, PaintEventArgs e)
        {

        }

        private void ShiftForm_Load(object sender, EventArgs e)
        {

            /*
             * When this form loads up, there's one of two cases; it is an empty shift (and
             * needs to be saved into the text file) OR it is a shift with preloaded information
             * and then it still needs to be saved/replace the actua shift in the form
             */
            MessageBox.Show("Attempted to load in: " + shiftFileName);
            if (shiftFileName == "")
            {
                MessageBox.Show("No file detected, loading in default");
                //shiftFileName = "C:/Users/bboyf/OneDrive/Desktop/CODE/LetsDoThisOneMoreTime/shift_scheduler_bot/SchedulerFormApp/JSON_files/Workers.json";
            }
            shiftFileRaw = File.ReadAllText(shiftFileName);
        }

        private void SaveShift_Button_Click(object sender, EventArgs e)
        {
            // make an object of the shift
            // export the object into the text file

        }

        private void CancelShift_Button_Click(object sender, EventArgs e)
        {
            // Simply closes the shift UI window without making any changes
            this.Close();
        }
        private void ShiftForm_EscapeKeyDown(object sender, KeyEventArgs e)
        {
            // Shortcut for closing the changes window
            if (e.KeyCode == Keys.Escape)
            {
                this.Close();
            }
        }

        private void makeShiftObject()
        {
            string workerName = "";
            string monthName = "";
            string dayName = "";
            int dayNum =;
            int startHour;
            int endHour;
            ShiftClass shiftObj = new ShiftClass()
        }
    }
}

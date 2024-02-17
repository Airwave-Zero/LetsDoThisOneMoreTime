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
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace scheduler_test1
{
    public partial class ShiftForm : Form
    {
        private string shiftFileName;
        private string shiftFileRaw;
        private string workerName;
        private string monthName;
        private string dayName;
        private int dayNum;
        private double shiftStartTime;
        private double shiftEndTime;
        private ShiftClass currentShift;
        public ShiftForm(string fileName = "")
        {
            shiftFileName = fileName;
            workerName = "";
            monthName = "";
            dayName = "";
            dayNum = 1;
            shiftStartTime = 0.0;
            shiftEndTime = 0.0;
            InitializeComponent();
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
            currentShift = makeShiftObject();
        }

        private void SaveShift_Button_Click(object sender, EventArgs e)
        /* This method handles when the user wants to save the shift. This method will create
         * a new shift object with all of the current user inputs, writes it to the shift file, and then
         * closes the window. */
        { 
            currentShift = makeShiftObject();
            //WRITE TO THE RAW TEXT FILE SOMEHOW
            string output = JsonConvert.SerializeObject(currentShift);
            // find the correct json object to override or write over
            File.WriteAllText(shiftFileName, output);
            this.Close();


            shiftFileRaw = File.ReadAllText(shiftFileName);
            string jsonShiftString = File.ReadAllText(shiftFileName);
            var test = JsonConvert.DeserializeObject<ShiftClass>(jsonShiftString);

            var json1 = "{ \"name\" : \"sai\", \"age\" : 22, \"salary\" : 25000}";
            var json2 = "{ \"name\" : \"sai\", \"age\" : 23, \"Gender\" : \"male\"}";

            var object1 = JObject.Parse(json1);
            var object2 = JObject.Parse(json2);

            foreach (var prop in object2.Properties())
            {
                var targetProperty = object1.Property(prop.Name);

                if (targetProperty == null)
                {
                    object1.Add(prop.Name, prop.Value);
                }
                else
                {
                    targetProperty.Value = prop.Value;
                }
            }

            var result = object1.ToString(Formatting.None);
            /*
            dataGridView1.DataSource = JsonConvert.DeserializeObject<DataTable>(jsonString);
            dataGridView1.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.AllCells;
            dataGridView1.DefaultCellStyle.WrapMode = DataGridViewTriState.True;
            */
            //https://stackoverflow.com/questions/29093055/update-json-object-in-c-sharp

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

        private ShiftClass makeShiftObject()
        /* This method creates a shift object based on whatever is in the UI
        */
        {
            var checkedStart = startPanel.Controls.OfType<RadioButton>().FirstOrDefault(r => r.Checked);
            var checkedEnd = endPanel.Controls.OfType<RadioButton>().FirstOrDefault(r => r.Checked);
            //string workerName = dropdown_WorkerName.SelectedValue.ToString();
            string workerName = dropdown_WorkerName.Text; 
            string startText = checkedStart.Text;
            string endText = checkedEnd.Text;
            shiftStartTime = getMilitaryConversion(startText);
            shiftEndTime = getMilitaryConversion(endText);

            ShiftClass shiftObj = new ShiftClass();
            shiftObj.setStartHour(shiftStartTime);
            shiftObj.setEndHour(shiftEndTime);
            shiftObj.setWorkerName(workerName);
            return shiftObj;
        }

        private double getMilitaryConversion(string baseTimeString)
        /* This is a helper function that takes in the radio button string and converts it into
        a military double and returns it. This also handles if the user put in a custom time for either panel.
         */
        {
            double militaryTime = 0.0;
            string convertedString = baseTimeString;
            if (baseTimeString.Equals("Custom"))
            {
                militaryTime = startCustomTextBox.Text.Equals("") ? Convert.ToDouble(endCustomTextBox.Text) :
                    Convert.ToDouble(startCustomTextBox.Text);
                convertedString = startCustomTextBox.Text.Equals("") ? endCustomTextBox.Text :
                    startCustomTextBox.Text;
            }
            else
            {
                militaryTime = Convert.ToDouble(baseTimeString.Substring(0, baseTimeString.IndexOf(":")));
            }
            
  
            if (convertedString.Contains(":30"))
            {
                militaryTime += .5;
            }
            else if (convertedString.Contains(":15"))
            {
                militaryTime += .25;
            }
            else if (convertedString.Contains(":45"))
            {
                militaryTime += .75;
            }

            if (convertedString.Contains("PM"))
            {
                militaryTime += 12; // basically this means we are using military time
            }
            return militaryTime;
        }
    }
}

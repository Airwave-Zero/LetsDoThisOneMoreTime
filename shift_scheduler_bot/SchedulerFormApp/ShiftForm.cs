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
using System.Net;

namespace scheduler_test1
{
    public partial class ShiftForm : Form
    {
        private string shiftFileName;
        private string shiftFileRaw;
        private string workerFileName;
        private string workerFileRaw;
        private string shiftWorkerName;
        private List<String> listWorkerNames;
        private string shiftMonthName;
        private string shiftDayName;
        private string[] daysOfWeek = { "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" };
        private int shiftDayNum;
        private double shiftStartTime;
        private double shiftEndTime;
        private ShiftClass currentShift;
        public ShiftForm(string fileName = "")
        {
            shiftFileName = fileName;
            shiftWorkerName = "";
            workerFileName = "";
            shiftMonthName = "";
            shiftDayName = "";
            shiftDayNum = 1;
            shiftStartTime = 0.0;
            shiftEndTime = 0.0;
            listWorkerNames = new List<String>();
            InitializeComponent();
        }

        private void ShiftForm_Load(object sender, EventArgs e)
        {

            /*
             * When this form loads up, there's one of two cases; it is an empty shift (and
             * needs to be saved into the text file) OR it is a shift with preloaded information
             * and then it still needs to be saved/replace the actua shift in the form
            MessageBox.Show("Attempted to load in shift: " + shiftFileName);
            if (shiftFileName == "")
            {
                MessageBox.Show("No file detected, loading in default");
                //shiftFileName = "C:/Users/bboyf/OneDrive/Desktop/CODE/LetsDoThisOneMoreTime/shift_scheduler_bot/SchedulerFormApp/JSON_files/Workers.json";
            }
            shiftFileRaw = File.ReadAllText(shiftFileName);
            */
            if (workerFileName == "")
            {
                //MessageBox.Show("No file detected, loading in default");
                workerFileName = "C:/Users/bboyf/OneDrive/Desktop/CODE/LetsDoThisOneMoreTime/shift_scheduler_bot/SchedulerFormApp/JSON_files/Workers.json";
            }
            if (shiftFileName == "")
            {
                shiftFileName = "C:/Users/bboyf/OneDrive/Desktop/CODE/LetsDoThisOneMoreTime/shift_scheduler_bot/SchedulerFormApp/JSON_files/Schedules/ScheduleJan8_14.json";
            }
            string jsonString = File.ReadAllText(workerFileName);
            workerFileRaw = jsonString;
            JArray workersArr = JArray.Parse(jsonString);
            foreach (JObject item in workersArr)
            {
                string currName = item.GetValue("Name").ToString();
                listWorkerNames.Add(currName);
                dropdown_WorkerName.Items.Add(currName);
            }
            foreach (string day in daysOfWeek)
            {
                dropdown_ShiftDayName.Items.Add(day);
            }
            dropdown_WorkerName.SelectedItem = dropdown_WorkerName.Items[0];
            dropdown_ShiftDayName.SelectedItem = dropdown_ShiftDayName.Items[0];
            shiftWorkerName = dropdown_WorkerName.SelectedItem.ToString().Split()[0];
            shiftDayName = dropdown_ShiftDayName.SelectedItem.ToString();
            currentShift = makeShiftObject();
        }

        private void SaveShift_Button_Click(object sender, EventArgs e)
        /* This method handles when the user wants to save the shift. This method will create
         * a new shift object with all of the current user inputs, writes it to the shift file, and then
         * closes the window. */
        {
            currentShift = makeShiftObject(); // grabs the UI elements and puts them in one easy to navigate object
            string jsonShiftString = File.ReadAllText(shiftFileName);

            var shiftObj = JObject.Parse(jsonShiftString);
            bool foundShift = false; // used to see if a new shift needs to be added or not
            bool deleteShift = checkbox_DeleteShift.Checked;
            // Iterate through each of the days in the JSON file
            foreach (var day in shiftObj.Children().Children()["Days"].Children())
            {
                string currDayName = day["Name"].ToString();
                int deleteCounter = -1;
                int deleteIndex = -1;
                // first check if the day is corresponding, then if so, go through the list of
                // current workers and add them
                if (shiftDayName == currDayName)
                {
                    foreach (var worker in day["Workers"])
                    {
                        // If they found the workers name, update the times for their shift
                        deleteCounter++;
                        var t1 = worker[0];
                        if (shiftWorkerName == worker.First.ToString())
                        {
                            if(deleteShift && Convert.ToString(currentShift.getStartHour()) == worker[1].ToString()
                                && Convert.ToString(currentShift.getEndHour()) == worker[2].ToString())
                            {
                                deleteIndex = deleteCounter;
                            }
                            worker[1] = currentShift.getStartHour().ToString();
                            worker[2] = currentShift.getEndHour().ToString();
                            foundShift = true;
                        }
                    }
                    // If the shift wasn't found, append the shift to the list of shifts
                    var allWorkersArr = day["Workers"];
                    var allWorkersJArr = (JArray)allWorkersArr;
                    if (!foundShift)
                    {
                        string[] newShift = { shiftWorkerName, currentShift.getStartHour().ToString(), currentShift.getEndHour().ToString() };
                        string output = JsonConvert.SerializeObject(newShift);
                        allWorkersJArr.Insert(day["Workers"].Count(), JToken.Parse(output));
                    }
                    if(deleteShift && deleteIndex > -1)
                    {
                        allWorkersJArr.RemoveAt(deleteIndex);
                    }
                    deleteCounter = 0;
                }
            }
            string shiftObjAsStr = JsonConvert.SerializeObject(shiftObj).ToString();
            // write it back to the file
            File.WriteAllText(shiftFileName, shiftObjAsStr);
            this.Close();
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
                militaryTime = Convert.ToDouble(baseTimeString.Substring(0, baseTimeString.IndexOf(" ")));
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

        private void dropdown_ShiftDayName_SelectedIndexChanged(object sender, EventArgs e)
        {
            shiftDayName = dropdown_ShiftDayName.Text.ToString();
        }

        private void dropdown_WorkerName_SelectedIndexChanged(object sender, EventArgs e)
        {
            shiftWorkerName = dropdown_WorkerName.Text.ToString();
        }
    }
}

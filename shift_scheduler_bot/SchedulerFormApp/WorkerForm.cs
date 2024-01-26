using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Runtime.Remoting.Contexts;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;


namespace scheduler_test1
{
    public partial class WorkerForm : Form
    {
        public WorkerForm()
        {
            InitializeComponent();
        }

        private void dataGridView1_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void WorkerForm_Load(object sender, EventArgs e)
        {
            string jsonString = File.ReadAllText("C:/Users/bboyf/OneDrive/Desktop/CODE/LetsDoThisOneMoreTime/shift_scheduler_bot/SchedulerFormApp/JSON_files/Workers.json");
            dataGridView1.DataSource = JsonConvert.DeserializeObject<DataTable>(jsonString);
        }
    }
}
    public class Employee
{
    public int age;
    public string status;
    public string experience;
    public string phone;
    public string[] notes;
    public string[] busy;
}

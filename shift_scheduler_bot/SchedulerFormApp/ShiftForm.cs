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
            if (shiftFileName != "") 
            { 
                shiftFileRaw = shiftFileName; 
            }
            InitializeComponent();
        }

        private void panel1_Paint(object sender, PaintEventArgs e)
        {

        }

        private void ShiftForm_Load(object sender, EventArgs e)
        {

        }
    }
}

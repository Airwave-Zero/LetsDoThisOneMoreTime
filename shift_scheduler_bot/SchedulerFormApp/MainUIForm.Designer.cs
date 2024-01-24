using System.Drawing;
using System.Windows.Forms;

namespace scheduler_test1
{
    partial class MainUIForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.button5 = new System.Windows.Forms.Button();
            this.button6 = new System.Windows.Forms.Button();
            this.button4 = new System.Windows.Forms.Button();
            this.panel1 = new System.Windows.Forms.Panel();
            this.Next = new System.Windows.Forms.Button();
            this.Previous = new System.Windows.Forms.Button();
            this.richTextBox1 = new System.Windows.Forms.RichTextBox();
            this.panel2 = new System.Windows.Forms.Panel();
            this.panel10 = new System.Windows.Forms.Panel();
            this.panel9 = new System.Windows.Forms.Panel();
            this.panel11 = new System.Windows.Forms.Panel();
            this.panel8 = new System.Windows.Forms.Panel();
            this.panel12 = new System.Windows.Forms.Panel();
            this.panel7 = new System.Windows.Forms.Panel();
            this.panel13 = new System.Windows.Forms.Panel();
            this.panel6 = new System.Windows.Forms.Panel();
            this.panel14 = new System.Windows.Forms.Panel();
            this.panel5 = new System.Windows.Forms.Panel();
            this.panel15 = new System.Windows.Forms.Panel();
            this.panel4 = new System.Windows.Forms.Panel();
            this.panel16 = new System.Windows.Forms.Panel();
            this.panel3 = new System.Windows.Forms.Panel();
            this.fileToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.loadScheduleToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.exportScheduleAsJSONToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.exportScheduleToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.saveScheduleToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.workersToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.viewWorkersToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.addEditWorkersToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.addEditRulesToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.addViewDaysOffToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.importWorkersToolStripMenuItem1 = new System.Windows.Forms.ToolStripMenuItem();
            this.exportWorkersToolStripMenuItem1 = new System.Windows.Forms.ToolStripMenuItem();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.textBox2 = new System.Windows.Forms.TextBox();
            this.textBox3 = new System.Windows.Forms.TextBox();
            this.textBox4 = new System.Windows.Forms.TextBox();
            this.textBox5 = new System.Windows.Forms.TextBox();
            this.textBox6 = new System.Windows.Forms.TextBox();
            this.textBox7 = new System.Windows.Forms.TextBox();
            this.panel1.SuspendLayout();
            this.panel2.SuspendLayout();
            this.menuStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // button5
            // 
            this.button5.Location = new System.Drawing.Point(785, 10);
            this.button5.Name = "button5";
            this.button5.Size = new System.Drawing.Size(95, 27);
            this.button5.TabIndex = 6;
            this.button5.Text = "Add Shift";
            this.button5.UseVisualStyleBackColor = true;
            this.button5.Click += new System.EventHandler(this.button5_Click);
            // 
            // button6
            // 
            this.button6.Enabled = false;
            this.button6.Location = new System.Drawing.Point(892, 10);
            this.button6.Name = "button6";
            this.button6.Size = new System.Drawing.Size(140, 27);
            this.button6.TabIndex = 7;
            this.button6.Text = "Edit/Delete Shift";
            this.button6.UseVisualStyleBackColor = true;
            this.button6.Click += new System.EventHandler(this.button6_Click);
            // 
            // button4
            // 
            this.button4.Location = new System.Drawing.Point(1044, 10);
            this.button4.Name = "button4";
            this.button4.Size = new System.Drawing.Size(152, 27);
            this.button4.TabIndex = 5;
            this.button4.Text = "Generate Schedule";
            this.button4.UseVisualStyleBackColor = true;
            this.button4.Click += new System.EventHandler(this.button4_Click);
            // 
            // panel1
            // 
            this.panel1.Controls.Add(this.Next);
            this.panel1.Controls.Add(this.Previous);
            this.panel1.Controls.Add(this.richTextBox1);
            this.panel1.Controls.Add(this.button5);
            this.panel1.Controls.Add(this.button4);
            this.panel1.Controls.Add(this.button6);
            this.panel1.Location = new System.Drawing.Point(12, 31);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(1207, 46);
            this.panel1.TabIndex = 9;
            // 
            // Next
            // 
            this.Next.Font = new System.Drawing.Font("Microsoft Sans Serif", 10F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Next.Location = new System.Drawing.Point(746, 10);
            this.Next.Name = "Next";
            this.Next.Size = new System.Drawing.Size(27, 27);
            this.Next.TabIndex = 0;
            this.Next.Text = "▶";
            this.Next.UseVisualStyleBackColor = true;
            // 
            // Previous
            // 
            this.Previous.Font = new System.Drawing.Font("Microsoft Sans Serif", 10F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Previous.Location = new System.Drawing.Point(434, 10);
            this.Previous.Name = "Previous";
            this.Previous.Size = new System.Drawing.Size(27, 27);
            this.Previous.TabIndex = 9;
            this.Previous.Text = "◀";
            this.Previous.UseVisualStyleBackColor = true;
            this.Previous.Click += new System.EventHandler(this.Previous_Click);
            // 
            // richTextBox1
            // 
            this.richTextBox1.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.richTextBox1.Location = new System.Drawing.Point(467, 10);
            this.richTextBox1.Name = "richTextBox1";
            this.richTextBox1.ReadOnly = true;
            this.richTextBox1.ScrollBars = System.Windows.Forms.RichTextBoxScrollBars.None;
            this.richTextBox1.Size = new System.Drawing.Size(273, 27);
            this.richTextBox1.TabIndex = 8;
            this.richTextBox1.Text = "Month D1-D7 Year";
            // 
            // panel2
            // 
            this.panel2.Controls.Add(this.panel10);
            this.panel2.Controls.Add(this.panel9);
            this.panel2.Controls.Add(this.panel11);
            this.panel2.Controls.Add(this.panel8);
            this.panel2.Controls.Add(this.panel12);
            this.panel2.Controls.Add(this.panel7);
            this.panel2.Controls.Add(this.panel13);
            this.panel2.Controls.Add(this.panel6);
            this.panel2.Controls.Add(this.panel14);
            this.panel2.Controls.Add(this.panel5);
            this.panel2.Controls.Add(this.panel15);
            this.panel2.Controls.Add(this.panel4);
            this.panel2.Controls.Add(this.panel16);
            this.panel2.Controls.Add(this.panel3);
            this.panel2.Location = new System.Drawing.Point(12, 112);
            this.panel2.Name = "panel2";
            this.panel2.Size = new System.Drawing.Size(1207, 645);
            this.panel2.TabIndex = 10;
            this.panel2.Paint += new System.Windows.Forms.PaintEventHandler(this.panel2_Paint);
            // 
            // panel10
            // 
            this.panel10.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel10.Location = new System.Drawing.Point(1044, 265);
            this.panel10.Name = "panel10";
            this.panel10.Size = new System.Drawing.Size(152, 377);
            this.panel10.TabIndex = 3;
            // 
            // panel9
            // 
            this.panel9.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel9.Location = new System.Drawing.Point(1044, 3);
            this.panel9.Name = "panel9";
            this.panel9.Size = new System.Drawing.Size(152, 256);
            this.panel9.TabIndex = 1;
            // 
            // panel11
            // 
            this.panel11.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel11.Location = new System.Drawing.Point(871, 265);
            this.panel11.Name = "panel11";
            this.panel11.Size = new System.Drawing.Size(152, 377);
            this.panel11.TabIndex = 4;
            // 
            // panel8
            // 
            this.panel8.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel8.Location = new System.Drawing.Point(871, 3);
            this.panel8.Name = "panel8";
            this.panel8.Size = new System.Drawing.Size(152, 256);
            this.panel8.TabIndex = 1;
            // 
            // panel12
            // 
            this.panel12.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel12.Location = new System.Drawing.Point(698, 265);
            this.panel12.Name = "panel12";
            this.panel12.Size = new System.Drawing.Size(152, 377);
            this.panel12.TabIndex = 5;
            // 
            // panel7
            // 
            this.panel7.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel7.Location = new System.Drawing.Point(698, 3);
            this.panel7.Name = "panel7";
            this.panel7.Size = new System.Drawing.Size(152, 256);
            this.panel7.TabIndex = 1;
            // 
            // panel13
            // 
            this.panel13.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel13.Location = new System.Drawing.Point(525, 265);
            this.panel13.Name = "panel13";
            this.panel13.Size = new System.Drawing.Size(152, 377);
            this.panel13.TabIndex = 6;
            // 
            // panel6
            // 
            this.panel6.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel6.Location = new System.Drawing.Point(525, 3);
            this.panel6.Name = "panel6";
            this.panel6.Size = new System.Drawing.Size(152, 256);
            this.panel6.TabIndex = 1;
            // 
            // panel14
            // 
            this.panel14.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel14.Location = new System.Drawing.Point(352, 265);
            this.panel14.Name = "panel14";
            this.panel14.Size = new System.Drawing.Size(152, 377);
            this.panel14.TabIndex = 7;
            // 
            // panel5
            // 
            this.panel5.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel5.Location = new System.Drawing.Point(352, 3);
            this.panel5.Name = "panel5";
            this.panel5.Size = new System.Drawing.Size(152, 256);
            this.panel5.TabIndex = 1;
            // 
            // panel15
            // 
            this.panel15.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel15.Location = new System.Drawing.Point(179, 265);
            this.panel15.Name = "panel15";
            this.panel15.Size = new System.Drawing.Size(152, 377);
            this.panel15.TabIndex = 8;
            // 
            // panel4
            // 
            this.panel4.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel4.Location = new System.Drawing.Point(179, 3);
            this.panel4.Name = "panel4";
            this.panel4.Size = new System.Drawing.Size(152, 256);
            this.panel4.TabIndex = 1;
            // 
            // panel16
            // 
            this.panel16.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel16.Location = new System.Drawing.Point(6, 265);
            this.panel16.Name = "panel16";
            this.panel16.Size = new System.Drawing.Size(152, 377);
            this.panel16.TabIndex = 2;
            // 
            // panel3
            // 
            this.panel3.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panel3.Location = new System.Drawing.Point(6, 3);
            this.panel3.Name = "panel3";
            this.panel3.Size = new System.Drawing.Size(152, 256);
            this.panel3.TabIndex = 0;
            // 
            // fileToolStripMenuItem
            // 
            this.fileToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.loadScheduleToolStripMenuItem,
            this.exportScheduleAsJSONToolStripMenuItem,
            this.exportScheduleToolStripMenuItem,
            this.saveScheduleToolStripMenuItem});
            this.fileToolStripMenuItem.Name = "fileToolStripMenuItem";
            this.fileToolStripMenuItem.Size = new System.Drawing.Size(46, 24);
            this.fileToolStripMenuItem.Text = "File";
            // 
            // loadScheduleToolStripMenuItem
            // 
            this.loadScheduleToolStripMenuItem.Name = "loadScheduleToolStripMenuItem";
            this.loadScheduleToolStripMenuItem.Size = new System.Drawing.Size(256, 26);
            this.loadScheduleToolStripMenuItem.Text = "Import Schedule";
            // 
            // exportScheduleAsJSONToolStripMenuItem
            // 
            this.exportScheduleAsJSONToolStripMenuItem.Name = "exportScheduleAsJSONToolStripMenuItem";
            this.exportScheduleAsJSONToolStripMenuItem.Size = new System.Drawing.Size(256, 26);
            this.exportScheduleAsJSONToolStripMenuItem.Text = "Export Schedule as JSON";
            // 
            // exportScheduleToolStripMenuItem
            // 
            this.exportScheduleToolStripMenuItem.Name = "exportScheduleToolStripMenuItem";
            this.exportScheduleToolStripMenuItem.Size = new System.Drawing.Size(256, 26);
            this.exportScheduleToolStripMenuItem.Text = "Export Schedule as PNG ";
            this.exportScheduleToolStripMenuItem.Click += new System.EventHandler(this.exportScheduleToolStripMenuItem_Click);
            // 
            // saveScheduleToolStripMenuItem
            // 
            this.saveScheduleToolStripMenuItem.Name = "saveScheduleToolStripMenuItem";
            this.saveScheduleToolStripMenuItem.ShortcutKeys = ((System.Windows.Forms.Keys)((System.Windows.Forms.Keys.Control | System.Windows.Forms.Keys.S)));
            this.saveScheduleToolStripMenuItem.Size = new System.Drawing.Size(256, 26);
            this.saveScheduleToolStripMenuItem.Text = "Save Schedule";
            // 
            // workersToolStripMenuItem
            // 
            this.workersToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.viewWorkersToolStripMenuItem,
            this.addEditWorkersToolStripMenuItem,
            this.addEditRulesToolStripMenuItem,
            this.addViewDaysOffToolStripMenuItem,
            this.importWorkersToolStripMenuItem1,
            this.exportWorkersToolStripMenuItem1});
            this.workersToolStripMenuItem.Name = "workersToolStripMenuItem";
            this.workersToolStripMenuItem.Size = new System.Drawing.Size(76, 24);
            this.workersToolStripMenuItem.Text = "Workers";
            // 
            // viewWorkersToolStripMenuItem
            // 
            this.viewWorkersToolStripMenuItem.Name = "viewWorkersToolStripMenuItem";
            this.viewWorkersToolStripMenuItem.Size = new System.Drawing.Size(224, 26);
            this.viewWorkersToolStripMenuItem.Text = "View Workers";
            this.viewWorkersToolStripMenuItem.Click += new System.EventHandler(this.viewWorkersToolStripMenuItem_Click);
            // 
            // addEditWorkersToolStripMenuItem
            // 
            this.addEditWorkersToolStripMenuItem.Name = "addEditWorkersToolStripMenuItem";
            this.addEditWorkersToolStripMenuItem.Size = new System.Drawing.Size(224, 26);
            this.addEditWorkersToolStripMenuItem.Text = "Add/Edit Workers";
            // 
            // addEditRulesToolStripMenuItem
            // 
            this.addEditRulesToolStripMenuItem.Name = "addEditRulesToolStripMenuItem";
            this.addEditRulesToolStripMenuItem.Size = new System.Drawing.Size(224, 26);
            this.addEditRulesToolStripMenuItem.Text = "Add/Edit Rules";
            // 
            // addViewDaysOffToolStripMenuItem
            // 
            this.addViewDaysOffToolStripMenuItem.Name = "addViewDaysOffToolStripMenuItem";
            this.addViewDaysOffToolStripMenuItem.Size = new System.Drawing.Size(224, 26);
            this.addViewDaysOffToolStripMenuItem.Text = "Add/View Days Off";
            // 
            // importWorkersToolStripMenuItem1
            // 
            this.importWorkersToolStripMenuItem1.Name = "importWorkersToolStripMenuItem1";
            this.importWorkersToolStripMenuItem1.Size = new System.Drawing.Size(224, 26);
            this.importWorkersToolStripMenuItem1.Text = "Import Workers";
            // 
            // exportWorkersToolStripMenuItem1
            // 
            this.exportWorkersToolStripMenuItem1.Name = "exportWorkersToolStripMenuItem1";
            this.exportWorkersToolStripMenuItem1.Size = new System.Drawing.Size(224, 26);
            this.exportWorkersToolStripMenuItem1.Text = "Export Workers";
            // 
            // menuStrip1
            // 
            this.menuStrip1.ImageScalingSize = new System.Drawing.Size(20, 20);
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.fileToolStripMenuItem,
            this.workersToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(1231, 28);
            this.menuStrip1.TabIndex = 8;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // textBox1
            // 
            this.textBox1.BackColor = this.BackColor;
            this.textBox1.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.textBox1.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.textBox1.Location = new System.Drawing.Point(18, 83);
            this.textBox1.Name = "textBox1";
            this.textBox1.ReadOnly = true;
            this.textBox1.Size = new System.Drawing.Size(152, 23);
            this.textBox1.TabIndex = 11;
            this.textBox1.Text = "Sunday";
            this.textBox1.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // textBox2
            // 
            this.textBox2.BackColor = this.BackColor;
            this.textBox2.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.textBox2.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.textBox2.Location = new System.Drawing.Point(191, 84);
            this.textBox2.Name = "textBox2";
            this.textBox2.ReadOnly = true;
            this.textBox2.Size = new System.Drawing.Size(152, 23);
            this.textBox2.TabIndex = 12;
            this.textBox2.Text = "Monday";
            this.textBox2.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // textBox3
            // 
            this.textBox3.BackColor = this.BackColor;
            this.textBox3.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.textBox3.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.textBox3.Location = new System.Drawing.Point(364, 84);
            this.textBox3.Name = "textBox3";
            this.textBox3.ReadOnly = true;
            this.textBox3.Size = new System.Drawing.Size(152, 23);
            this.textBox3.TabIndex = 13;
            this.textBox3.Text = "Tuesday";
            this.textBox3.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // textBox4
            // 
            this.textBox4.BackColor = this.BackColor;
            this.textBox4.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.textBox4.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.textBox4.Location = new System.Drawing.Point(537, 85);
            this.textBox4.Name = "textBox4";
            this.textBox4.ReadOnly = true;
            this.textBox4.Size = new System.Drawing.Size(152, 23);
            this.textBox4.TabIndex = 14;
            this.textBox4.Text = "Wednesday";
            this.textBox4.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // textBox5
            // 
            this.textBox5.BackColor = this.BackColor;
            this.textBox5.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.textBox5.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.textBox5.Location = new System.Drawing.Point(710, 84);
            this.textBox5.Name = "textBox5";
            this.textBox5.ReadOnly = true;
            this.textBox5.Size = new System.Drawing.Size(152, 23);
            this.textBox5.TabIndex = 15;
            this.textBox5.Text = "Thursday";
            this.textBox5.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // textBox6
            // 
            this.textBox6.BackColor = this.BackColor;
            this.textBox6.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.textBox6.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.textBox6.Location = new System.Drawing.Point(883, 84);
            this.textBox6.Name = "textBox6";
            this.textBox6.ReadOnly = true;
            this.textBox6.Size = new System.Drawing.Size(152, 23);
            this.textBox6.TabIndex = 16;
            this.textBox6.Text = "Friday";
            this.textBox6.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // textBox7
            // 
            this.textBox7.BackColor = this.BackColor;
            this.textBox7.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.textBox7.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.textBox7.Location = new System.Drawing.Point(1056, 83);
            this.textBox7.Name = "textBox7";
            this.textBox7.ReadOnly = true;
            this.textBox7.Size = new System.Drawing.Size(152, 23);
            this.textBox7.TabIndex = 17;
            this.textBox7.Text = "Saturday";
            this.textBox7.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1231, 769);
            this.Controls.Add(this.textBox7);
            this.Controls.Add(this.textBox6);
            this.Controls.Add(this.textBox5);
            this.Controls.Add(this.textBox4);
            this.Controls.Add(this.textBox3);
            this.Controls.Add(this.textBox2);
            this.Controls.Add(this.textBox1);
            this.Controls.Add(this.panel1);
            this.Controls.Add(this.panel2);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "Form1";
            this.Text = "Dpot Scheduler v1.0";
            this.panel1.ResumeLayout(false);
            this.panel2.ResumeLayout(false);
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.Button button5;
        private System.Windows.Forms.Button button6;
        private System.Windows.Forms.Button button4;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.Panel panel2;
        private System.Windows.Forms.ToolStripMenuItem fileToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem loadScheduleToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem exportScheduleAsJSONToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem exportScheduleToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem saveScheduleToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem workersToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem addEditWorkersToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem addEditRulesToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem addViewDaysOffToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem importWorkersToolStripMenuItem1;
        private System.Windows.Forms.ToolStripMenuItem exportWorkersToolStripMenuItem1;
        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.RichTextBox richTextBox1;
        private System.Windows.Forms.Button Previous;
        private System.Windows.Forms.Button Next;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.TextBox textBox2;
        private System.Windows.Forms.TextBox textBox3;
        private System.Windows.Forms.TextBox textBox4;
        private System.Windows.Forms.TextBox textBox5;
        private System.Windows.Forms.TextBox textBox6;
        private System.Windows.Forms.TextBox textBox7;
        private Panel panel3;
        private Panel panel9;
        private Panel panel8;
        private Panel panel7;
        private Panel panel6;
        private Panel panel5;
        private Panel panel4;
        private Panel panel10;
        private Panel panel11;
        private Panel panel12;
        private Panel panel13;
        private Panel panel14;
        private Panel panel15;
        private Panel panel16;
        private ToolStripMenuItem viewWorkersToolStripMenuItem;
    }
}


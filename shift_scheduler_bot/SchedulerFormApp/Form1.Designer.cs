namespace scheduler_test1
{
    partial class Form1
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
            this.Previous = new System.Windows.Forms.Button();
            this.richTextBox1 = new System.Windows.Forms.RichTextBox();
            this.panel2 = new System.Windows.Forms.Panel();
            this.Next = new System.Windows.Forms.Button();
            this.fileToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.loadScheduleToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.exportScheduleAsJSONToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.exportScheduleToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.saveScheduleToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.workersToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.addEditWorkersToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.addEditRulesToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.addViewDaysOffToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.importWorkersToolStripMenuItem1 = new System.Windows.Forms.ToolStripMenuItem();
            this.exportWorkersToolStripMenuItem1 = new System.Windows.Forms.ToolStripMenuItem();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.panel1.SuspendLayout();
            this.menuStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // button5
            // 
            this.button5.Location = new System.Drawing.Point(830, 7);
            this.button5.Name = "button5";
            this.button5.Size = new System.Drawing.Size(114, 28);
            this.button5.TabIndex = 6;
            this.button5.Text = "Add Shift";
            this.button5.UseVisualStyleBackColor = true;
            this.button5.Click += new System.EventHandler(this.button5_Click);
            // 
            // button6
            // 
            this.button6.Location = new System.Drawing.Point(950, 7);
            this.button6.Name = "button6";
            this.button6.Size = new System.Drawing.Size(114, 28);
            this.button6.TabIndex = 7;
            this.button6.Text = "Edit/Delete Shift";
            this.button6.UseVisualStyleBackColor = true;
            this.button6.Click += new System.EventHandler(this.button6_Click);
            // 
            // button4
            // 
            this.button4.Location = new System.Drawing.Point(1070, 7);
            this.button4.Name = "button4";
            this.button4.Size = new System.Drawing.Size(114, 28);
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
            this.panel1.Size = new System.Drawing.Size(1188, 46);
            this.panel1.TabIndex = 9;
            // 
            // Previous
            // 
            this.Previous.Font = new System.Drawing.Font("Microsoft Sans Serif", 10F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Previous.Location = new System.Drawing.Point(417, 10);
            this.Previous.Name = "Previous";
            this.Previous.Size = new System.Drawing.Size(26, 27);
            this.Previous.TabIndex = 9;
            this.Previous.Text = "◀";
            this.Previous.UseVisualStyleBackColor = true;
            this.Previous.Click += new System.EventHandler(this.Previous_Click);
            // 
            // richTextBox1
            // 
            this.richTextBox1.Location = new System.Drawing.Point(449, 10);
            this.richTextBox1.Name = "richTextBox1";
            this.richTextBox1.Size = new System.Drawing.Size(273, 27);
            this.richTextBox1.TabIndex = 8;
            this.richTextBox1.Text = "";
            // 
            // panel2
            // 
            this.panel2.Location = new System.Drawing.Point(12, 97);
            this.panel2.Name = "panel2";
            this.panel2.Size = new System.Drawing.Size(1176, 506);
            this.panel2.TabIndex = 10;
            // 
            // Next
            // 
            this.Next.Font = new System.Drawing.Font("Microsoft Sans Serif", 10F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Next.Location = new System.Drawing.Point(728, 10);
            this.Next.Name = "Next";
            this.Next.Size = new System.Drawing.Size(27, 27);
            this.Next.TabIndex = 0;
            this.Next.Text = "▶";
            this.Next.UseVisualStyleBackColor = true;
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
            this.addEditWorkersToolStripMenuItem,
            this.addEditRulesToolStripMenuItem,
            this.addViewDaysOffToolStripMenuItem,
            this.importWorkersToolStripMenuItem1,
            this.exportWorkersToolStripMenuItem1});
            this.workersToolStripMenuItem.Name = "workersToolStripMenuItem";
            this.workersToolStripMenuItem.Size = new System.Drawing.Size(76, 24);
            this.workersToolStripMenuItem.Text = "Workers";
            // 
            // addEditWorkersToolStripMenuItem
            // 
            this.addEditWorkersToolStripMenuItem.Name = "addEditWorkersToolStripMenuItem";
            this.addEditWorkersToolStripMenuItem.Size = new System.Drawing.Size(219, 26);
            this.addEditWorkersToolStripMenuItem.Text = "Add/Edit Workers";
            // 
            // addEditRulesToolStripMenuItem
            // 
            this.addEditRulesToolStripMenuItem.Name = "addEditRulesToolStripMenuItem";
            this.addEditRulesToolStripMenuItem.Size = new System.Drawing.Size(219, 26);
            this.addEditRulesToolStripMenuItem.Text = "Add/Edit Rules";
            // 
            // addViewDaysOffToolStripMenuItem
            // 
            this.addViewDaysOffToolStripMenuItem.Name = "addViewDaysOffToolStripMenuItem";
            this.addViewDaysOffToolStripMenuItem.Size = new System.Drawing.Size(219, 26);
            this.addViewDaysOffToolStripMenuItem.Text = "Add/View Days Off";
            // 
            // importWorkersToolStripMenuItem1
            // 
            this.importWorkersToolStripMenuItem1.Name = "importWorkersToolStripMenuItem1";
            this.importWorkersToolStripMenuItem1.Size = new System.Drawing.Size(219, 26);
            this.importWorkersToolStripMenuItem1.Text = "Import Workers";
            // 
            // exportWorkersToolStripMenuItem1
            // 
            this.exportWorkersToolStripMenuItem1.Name = "exportWorkersToolStripMenuItem1";
            this.exportWorkersToolStripMenuItem1.Size = new System.Drawing.Size(219, 26);
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
            this.menuStrip1.Size = new System.Drawing.Size(1200, 30);
            this.menuStrip1.TabIndex = 8;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1200, 674);
            this.Controls.Add(this.panel1);
            this.Controls.Add(this.panel2);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "Form1";
            this.Text = "Form1";
            this.panel1.ResumeLayout(false);
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
    }
}


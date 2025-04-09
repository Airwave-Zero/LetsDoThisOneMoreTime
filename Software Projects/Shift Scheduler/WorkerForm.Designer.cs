namespace scheduler_test1
{
    partial class WorkerForm
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
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.SaveButton = new System.Windows.Forms.Button();
            this.CancelChangesButton = new System.Windows.Forms.Button();
            this.WorkerFFN_Label = new System.Windows.Forms.Label();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.SuspendLayout();
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Location = new System.Drawing.Point(45, 96);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.RowHeadersWidth = 51;
            this.dataGridView1.RowTemplate.Height = 24;
            this.dataGridView1.Size = new System.Drawing.Size(1075, 413);
            this.dataGridView1.TabIndex = 0;
            this.dataGridView1.CellContentClick += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView1_CellContentClick);
            // 
            // SaveButton
            // 
            this.SaveButton.Location = new System.Drawing.Point(338, 46);
            this.SaveButton.Name = "SaveButton";
            this.SaveButton.Size = new System.Drawing.Size(159, 39);
            this.SaveButton.TabIndex = 1;
            this.SaveButton.Text = "Save Changes";
            this.SaveButton.UseVisualStyleBackColor = true;
            this.SaveButton.Click += new System.EventHandler(this.SaveButton_Click);
            // 
            // CancelChangesButton
            // 
            this.CancelChangesButton.Location = new System.Drawing.Point(647, 46);
            this.CancelChangesButton.Name = "CancelChangesButton";
            this.CancelChangesButton.Size = new System.Drawing.Size(159, 39);
            this.CancelChangesButton.TabIndex = 2;
            this.CancelChangesButton.Text = "Cancel Changes";
            this.CancelChangesButton.UseVisualStyleBackColor = true;
            this.CancelChangesButton.Click += new System.EventHandler(this.CancelButton_Click);
            // 
            // WorkerFFN_Label
            // 
            this.WorkerFFN_Label.AutoSize = true;
            this.WorkerFFN_Label.Font = new System.Drawing.Font("Microsoft Sans Serif", 14F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.WorkerFFN_Label.Location = new System.Drawing.Point(496, 7);
            this.WorkerFFN_Label.Name = "WorkerFFN_Label";
            this.WorkerFFN_Label.Size = new System.Drawing.Size(148, 29);
            this.WorkerFFN_Label.TabIndex = 3;
            this.WorkerFFN_Label.Text = "Loaded File:";
            // 
            // WorkerForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1144, 524);
            this.Controls.Add(this.WorkerFFN_Label);
            this.Controls.Add(this.CancelChangesButton);
            this.Controls.Add(this.SaveButton);
            this.Controls.Add(this.dataGridView1);
            this.KeyPreview = true;
            this.Name = "WorkerForm";
            this.Text = "WorkerForm";
            this.Load += new System.EventHandler(this.WorkerForm_Load);
            this.KeyDown += new System.Windows.Forms.KeyEventHandler(this.WorkerForm_EscapeKeyDown);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Button SaveButton;
        private System.Windows.Forms.Button CancelChangesButton;
        private System.Windows.Forms.Label WorkerFFN_Label;
    }
}
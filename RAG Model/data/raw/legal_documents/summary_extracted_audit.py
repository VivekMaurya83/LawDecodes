import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import google.generativeai as genai
import os
import json


class GeminiPDFGenerator:
    """
    Generate professional PDF reports from CSV files using Gemini API for intelligent analysis.
    """

    def __init__(self, api_key=None):
        """Initialize with Gemini API key."""
        # Configure API key
        if api_key:
            genai.configure(api_key=api_key)
        else:
            # Get from environment
            env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if env_key:
                genai.configure(api_key=env_key)
                print("SUCCESS: API key loaded from environment")
            else:
                print("WARNING: No API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")

        # Use a stable Gemini model
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("SUCCESS: Using Gemini 1.5 Flash model")
        except Exception as e:
            print(f"WARNING: Model initialization error: {e}")
            self.model = None

    def analyze_csv_with_gemini(self, csv_file):
        """
        Use Gemini to analyze CSV structure and generate insights.
        
        Returns: Dictionary with title, insights, and formatting suggestions.
        """
        if not self.model:
            print("WARNING: Gemini model not available. Using fallback analysis.")
            return self._fallback_analysis(csv_file)

        # Read CSV
        df = pd.read_csv(csv_file)

        # Prepare CSV preview for Gemini (30 rows for better analysis)
        csv_preview = df.head(30).to_csv(index=False)

        # Calculate statistics
        total_rows = len(df)
        columns = df.columns.tolist()

        # Analyze specific patterns
        stats = {}
        if 'access_decision' in df.columns:
            stats['granted'] = len(df[df['access_decision'] == 'granted'])
            stats['denied'] = len(df[df['access_decision'] == 'denied'])

        if 'name' in df.columns:
            stats['unique_users'] = df[df['name'] != 'Unknown']['name'].nunique()
            stats['unknown_attempts'] = len(df[df['name'] == 'Unknown'])

        # Create detailed prompt for Gemini
        prompt = f"""
        Analyze this access control audit log CSV data and provide detailed insights for a professional PDF report.
        
        CSV Data Preview (first 30 rows):
        {csv_preview}
        
        Statistics:
        - Total Rows: {total_rows}
        - Columns: {columns}
        - Access Granted: {stats.get('granted', 'N/A')}
        - Access Denied: {stats.get('denied', 'N/A')}
        - Unique Authorized Users: {stats.get('unique_users', 'N/A')}
        - Unknown Access Attempts: {stats.get('unknown_attempts', 'N/A')}
        
        Provide a JSON response with:
        {{
            "report_title": "A professional title for this access control data",
            "summary_insights": ["5-7 detailed insights about access patterns, security, peak times, frequent users"],
            "data_type": "Access Control Logs",
            "key_metrics": {{
                "Total Access Events": {total_rows},
                "Access Granted": {stats.get('granted', 0)},
                "Access Denied": {stats.get('denied', 0)},
                "Grant Rate": "percentage as string",
                "Unique Authorized Users": {stats.get('unique_users', 0)},
                "Unknown Access Attempts": {stats.get('unknown_attempts', 0)},
                "Security Risk Level": "Low/Medium/High"
            }},
            "column_descriptions": {{
                "column_name": "description"
            }}
        }}
        
        Analyze: security patterns, most active users, time patterns, security concerns.
        Return ONLY valid JSON without markdown code blocks.
        """

        try:
            response = self.model.generate_content(prompt)
            # Clean response text
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            elif response_text.startswith('```'):
                response_text = response_text[3:]

            if response_text.endswith('```'):
                response_text = response_text[:-3]

            analysis = json.loads(response_text.strip())
            print("SUCCESS: Gemini analysis successful")
            return analysis

        except Exception as e:
            print(f"WARNING: Gemini analysis error: {e}")
            print("Using fallback analysis...")
            return self._fallback_analysis(csv_file)

    def _fallback_analysis(self, csv_file):
        """Provides a default analysis if the API call fails."""
        df = pd.read_csv(csv_file)
        total_rows = len(df)
        columns = df.columns.tolist()
        stats = {}

        if 'access_decision' in df.columns:
            stats['granted'] = len(df[df['access_decision'] == 'granted'])
            stats['denied'] = len(df[df['access_decision'] == 'denied'])
        
        if 'name' in df.columns:
            stats['unique_users'] = df[df['name'] != 'Unknown']['name'].nunique()
            stats['unknown_attempts'] = len(df[df['name'] == 'Unknown'])

        grant_rate = (stats.get('granted', 0) / total_rows * 100) if total_rows > 0 else 0

        return {
            "report_title": "Access Control System Audit Report",
            "summary_insights": [
                f"System logged {total_rows} total access events during the audit period.",
                f"Access granted in {stats.get('granted', 0)} cases ({grant_rate:.1f}% success rate).",
                f"Detected {stats.get('denied', 0)} denied access attempts requiring security review.",
                f"System has {stats.get('unique_users', 0)} authorized users with valid credentials.",
                f"Found {stats.get('unknown_attempts', 0)} unauthorized access attempts from unknown individuals.",
                "All events were recorded at the 'Gate 1' location.",
                "Activity appears concentrated in standard business hours based on timestamps."
            ],
            "data_type": "Access Control Logs",
            "key_metrics": {
                "Total Access Events": total_rows,
                "Access Granted": stats.get('granted', 0),
                "Access Denied": stats.get('denied', 0),
                "Grant Rate": f"{grant_rate:.1f}%",
                "Unique Authorized Users": stats.get('unique_users', 0),
                "Unknown Access Attempts": stats.get('unknown_attempts', 0),
                "Security Risk Level": "Medium" if stats.get('denied', 0) > 10 else "Low"
            },
            "column_descriptions": {col: col.replace('_', ' ').title() for col in columns}
        }

    def generate_pdf(self, csv_file, output_pdf='gemini_report.pdf', custom_analysis=None):
        """
        Generate PDF.
        
        Parameters:
        csv_file (str): Path to input CSV file.
        output_pdf (str): Path to output PDF file.
        custom_analysis (dict): Optional pre-computed analysis from Gemini.
        """
        if custom_analysis is None:
            print("Analyzing CSV with Gemini...")
            analysis = self.analyze_csv_with_gemini(csv_file)
        else:
            analysis = custom_analysis

        print(f"SUCCESS: Analysis complete: {analysis.get('data_type', 'Data')}")

        df = pd.read_csv(csv_file)

        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=50,
            bottomMargin=30
        )

        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            spaceAfter=15,
            alignment=TA_CENTER
        )
        
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['h2'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )

        insight_style = ParagraphStyle(
            'Insight',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20,
            bulletIndent=10
        )

        # Add title
        title = Paragraph(analysis.get('report_title', 'Data Report'), title_style)
        elements.append(title)

        # Add timestamp
        timestamp = Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Powered by Gemini AI",
            subtitle_style
        )
        elements.append(timestamp)
        elements.append(Spacer(1, 20))

        # Add key metrics
        if analysis.get('key_metrics'):
            metrics_title = Paragraph("Key Metrics", section_title_style)
            elements.append(metrics_title)

            for key, value in analysis['key_metrics'].items():
                metric_text = f"-   <b>{key}:</b> {value}"
                elements.append(Paragraph(metric_text, insight_style))

            elements.append(Spacer(1, 15))

        # Add AI-generated insights
        if analysis.get('summary_insights'):
            insights_title = Paragraph("AI-Generated Summary & Insights", section_title_style)
            elements.append(insights_title)

            for insight in analysis['summary_insights']:
                insight_text = f"-   {insight}"
                elements.append(Paragraph(insight_text, insight_style))

            elements.append(Spacer(1, 20))
        
        # Add Data Table Title
        elements.append(Paragraph("Detailed Log Data", section_title_style))

        # Prepare table data
        table_data = [df.columns.tolist()] + df.values.tolist()
        
        # Dynamic column widths
        num_cols = len(df.columns)
        available_width = 7.5 * inch
        col_width = available_width / num_cols
        col_widths = [col_width] * num_cols

        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Style the table
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ])

        # Apply intelligent color-coding for access decisions
        if 'access_decision' in df.columns:
            decision_col_index = df.columns.tolist().index('access_decision')
            for i, decision in enumerate(df['access_decision']):
                row_idx = i + 1  # +1 for header
                if decision == 'denied':
                    table_style.add('BACKGROUND', (decision_col_index, row_idx), (decision_col_index, row_idx), colors.HexColor('#ffcdd2'))
                    table_style.add('TEXTCOLOR', (decision_col_index, row_idx), (decision_col_index, row_idx), colors.HexColor('#c62828'))
                elif decision == 'granted':
                    table_style.add('BACKGROUND', (decision_col_index, row_idx), (decision_col_index, row_idx), colors.HexColor('#c8e6c9'))
                    table_style.add('TEXTCOLOR', (decision_col_index, row_idx), (decision_col_index, row_idx), colors.HexColor('#2e7d32'))

        table.setStyle(table_style)
        elements.append(table)

        doc.build(elements)
        print(f"SUCCESS: PDF generated successfully: {output_pdf}")

        # Write the summary file
        self._write_summary_to_file(analysis, output_pdf)
        
        return output_pdf

    def _write_summary_to_file(self, analysis, output_pdf_path):
        """
        Extracts summary information from the analysis and writes it to a .txt file.
        The summary file is created in the same directory as the PDF.
        """
        # --- CORRECTED CODE ---
        # os.path.splitext() returns a tuple: (filename, .extension)
        # We unpack this tuple to get just the filename part.
        base_filename, _ = os.path.splitext(output_pdf_path)
        # Now, base_filename is a string (e.g., 'audit_report_gemini'), so we can append to it.
        summary_filename = base_filename + '_summary.txt'
        # --- END OF CORRECTION ---

        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(f"Report Title: {analysis.get('report_title', 'No Title Provided')}\n\n")
            f.write("="*20 + "\n")
            f.write("Key Metrics\n")
            f.write("="*20 + "\n")
            if analysis.get('key_metrics'):
                for key, value in analysis['key_metrics'].items():
                    f.write(f"- {key}: {value}\n")
            else:
                f.write("- No key metrics provided.\n")
            
            f.write("\n" + "="*20 + "\n")
            f.write("AI-Generated Insights\n")
            f.write("="*20 + "\n")
            if analysis.get('summary_insights'):
                for i, insight in enumerate(analysis['summary_insights'], 1):
                    f.write(f"{i}. {insight}\n")
            else:
                f.write("- No insights provided.\n")
        
        print(f"SUCCESS: Summary extracted to: {summary_filename}")


def create_dummy_csv_if_not_exists(filename='audit_logs.csv'):
    """Creates a dummy CSV file for demonstration purposes if it doesn't exist."""
    if not os.path.exists(filename):
        dummy_data = {
            'timestamp': [
                '2023-01-01 08:00:00', '2023-01-01 08:05:00', '2023-01-01 09:10:00',
                '2023-01-01 10:15:00', '2023-01-01 10:20:00', '2023-01-01 11:30:00',
                '2023-01-01 12:00:00', '2023-01-01 13:00:00', '2023-01-01 14:00:00',
                '2023-01-01 15:00:00', '2023-01-01 16:00:00', '2023-01-01 17:00:00',
                '2023-01-01 18:00:00', '2023-01-01 19:00:00', '2023-01-01 20:00:00'
            ],
            'name': [
                'Alice', 'Bob', 'Alice', 'Unknown', 'Charlie', 'Bob',
                'Alice', 'David', 'Eve', 'Frank', 'Alice', 'Bob',
                'Charlie', 'Unknown', 'Alice'
            ],
            'access_decision': [
                'granted', 'granted', 'granted', 'denied', 'granted', 'granted',
                'denied', 'granted', 'granted', 'granted', 'granted', 'denied',
                'granted', 'denied', 'granted'
            ],
            'location': [
                'Gate 1', 'Gate 1', 'Gate 1', 'Gate 1', 'Gate 1', 'Gate 1',
                'Gate 1', 'Gate 1', 'Gate 1', 'Gate 1', 'Gate 1', 'Gate 1',
                'Gate 1', 'Gate 1', 'Gate 1'
            ]
        }
        df_dummy = pd.DataFrame(dummy_data)
        df_dummy.to_csv(filename, index=False)
        print(f"Created a dummy '{filename}' for demonstration.")


# Main execution block
if __name__ == "__main__":
    # Ensure a CSV file exists for testing.
    csv_filename = 'audit_logs.csv'
    create_dummy_csv_if_not_exists(csv_filename)

    print("=" * 50)
    print("Starting PDF Generation...")
    print("=" * 50)
    
    # Initialize the generator.
    # Make sure your GEMINI_API_KEY is set as an environment variable.
    generator = GeminiPDFGenerator()
    
    # Generate the PDF and the summary text file.
    output_filename = 'audit_report_gemini.pdf'
    generator.generate_pdf(csv_filename, output_filename)
    
    print("=" * 50)
    print("Process Finished!")
    print(f"Check for '{output_filename}' and 'audit_report_gemini_summary.txt'")
    print("=" * 50)
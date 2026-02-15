import requests
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import os
from dotenv import load_dotenv

load_dotenv()

console = Console()

class WeatherAnalyzer:
    def __init__(self, city):
        self.city = city
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    def fetch_forecast(self):
        params = {
            'q': self.city,
            'appid': self.api_key,
            'units': 'imperial'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error fetching data: {e}[/red]")
            return None
    
    def analyze_data(self, data):
        if not data:
            return None
        
        temps = []
        conditions = []
        timestamps = []
        
        forecast_limit = min(32, len(data['list']))
        
        for item in data['list'][:forecast_limit]:
            temps.append(item['main']['temp'])
            conditions.append(item['weather'][0]['main'])
            timestamps.append(datetime.fromtimestamp(item['dt']))
        
        analysis = {
            'avg_temp': sum(temps) / len(temps),
            'max_temp': max(temps),
            'min_temp': min(temps),
            'temp_range': max(temps) - min(temps),
            'most_common_condition': max(set(conditions), key=conditions.count),
            'forecasts': list(zip(timestamps, temps, conditions))[:12]
        }
        
        return analysis
    
    def display_results(self, analysis):
        if not analysis:
            return
        
        summary = f"""
[cyan]City:[/cyan] {self.city}
[cyan]Average Temperature:[/cyan] {analysis['avg_temp']:.1f}°F
[cyan]High:[/cyan] {analysis['max_temp']:.1f}°F
[cyan]Low:[/cyan] {analysis['min_temp']:.1f}°F
[cyan]Temperature Range:[/cyan] {analysis['temp_range']:.1f}°F
[cyan]Most Common Condition:[/cyan] {analysis['most_common_condition']}
        """
        
        console.print(Panel(summary.strip(), title="4-Day Weather Analysis", border_style="blue"))
        
        table = Table(title=f"\n4-Day Forecast for {self.city}")
        table.add_column("Time", style="cyan")
        table.add_column("Temperature", style="magenta")
        table.add_column("Condition", style="green")
        
        for timestamp, temp, condition in analysis['forecasts']:
            table.add_row(
                timestamp.strftime("%m/%d %I:%M %p"),
                f"{temp:.1f}°F",
                condition
            )
        
        console.print(table)
        
        console.print("\n[bold]Temperature Trend (4 Days):[/bold]")
        temps = [temp for _, temp, _ in analysis['forecasts']]
        min_t, max_t = min(temps), max(temps)
        
        for timestamp, temp, _ in analysis['forecasts']:
            normalized = int((temp - min_t) / (max_t - min_t) * 30) if max_t != min_t else 15
            bar = '█' * normalized
            console.print(f"{timestamp.strftime('%m/%d %I%p'):11} | {bar} {temp:.1f}°F")
    
    def run(self):
        console.print(f"\n[bold green]Fetching 4-day weather data for {self.city}...[/bold green]\n")
        data = self.fetch_forecast()
        
        if data:
            analysis = self.analyze_data(data)
            self.display_results(analysis)
        else:
            console.print("[red]Failed to retrieve weather data[/red]")

def main():
    console.print("[bold cyan]4-Day Weather Analysis Tool[/bold cyan]")
    city = input("\nEnter city name: ").strip()
    
    if not city:
        console.print("[red]City name cannot be empty[/red]")
        return
    
    analyzer = WeatherAnalyzer(city)
    analyzer.run()
    
    while True:
        another = input("\nAnalyze another city? (y/n): ").lower()
        if another == 'y':
            city = input("Enter city name: ").strip()
            analyzer = WeatherAnalyzer(city)
            analyzer.run()
        else:
            console.print("\n[green]Thanks for using Weather Analyzer![/green]")
            break

if __name__ == "__main__":
    main()
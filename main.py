import typer
import can
from nhp10.app import create_app, socketio

def run_app(can_interface: str = typer.Argument(..., help="SocketCAN interface name"),
            host: str = typer.Option("127.0.0.1", help="Host to run the server on"),
            port: int = typer.Option(5000, help="Port to run the server on"),
            debug: bool = typer.Option(False, help="Run in debug mode")):
    """
    Run the CAN Bus Web Interface application.
    """
    try:
        can_bus = can.interface.Bus(channel=can_interface, bustype='socketcan')
        print(f"Connected to CAN interface: {can_interface}")
        
        app = create_app(can_bus)
        socketio.run(app, host=host, port=port, debug=debug)
    except can.CanError as e:
        print(f"Error connecting to CAN interface {can_interface}: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    typer.run(run_app)

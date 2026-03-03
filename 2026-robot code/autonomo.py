import wpilib
from wpilib.drive import DifferentialDrive
from phoenix5 import WPI_TalonSRX, FeedbackDevice, ControlMode, NeutralMode

class AutonomousTest1:
    """
    Teste 1(anda e shoota):
      - tração se move a 70% da velocidade por 3s
      - shooter atira por 10s na potencia maxima
      - Estado 2: Finaliza (motor parado).
    """
    def __init__(self, drive, shooter):
        self.drive      =   drive
        self.shooter = shooter
        self.state = 0
        self.start_time = 0

    def start(self):
        self.state = 0
        self.start_time = wpilib.Timer.getFPGATimestamp()

    def run(self):
        current_time = wpilib.Timer.getFPGATimestamp()
        match self.state:
            case 0:
                self.drive.arcadeDrive(0.3, 0) #move a tração
                if current_time - self.start_time >= 3.0:
                    self.state = 1
                    self.start_time = current_time
            case 1:
                self.drive.arcadeDrive(0, 0) #para a tração
                self.shooter.set(ControlMode.PercentOutput, 1)#shooter
                if current_time - self.start_time >= 10:
                    self.shooter.set(ControlMode.PercentOutput, 0.0)
                    self.state = 2
                    self.start_time = current_time
            case 2:
                self.drive.arcadeDrive(0, 0) #para a tração a tração
                self.garra.set(ControlMode.PercentOutput, 0.0)#desliga garra
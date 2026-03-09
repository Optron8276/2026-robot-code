import wpilib
from wpilib.drive import DifferentialDrive
from phoenix5 import WPI_TalonSRX, FeedbackDevice, ControlMode, NeutralMode, WPI_VictorSPX

class AutonomousTest1:
    """
    Teste 1:
      - Estado 0: Tração se move por 2 segundos a 70% de velocidade.
      - Estado 1: Motor parado por 1.5 segundos.
      - Estado 2: Finaliza (motor parado).
    """
    def __init__(self, drive , shooter, shooter_assist, indexer):
        self.drive          = drive
        self.shooter        = shooter
        self.shooter_assist = shooter_assist
        self.indexer        = indexer
        self.state          = 0
        self.start_time     = 0

    def start(self):
        self.state = 0
        self.start_time = wpilib.Timer.getFPGATimestamp()

    def run(self):
        current_time = wpilib.Timer.getFPGATimestamp()
        match self.state:
            case 0:
                self.drive.arcadeDrive(0.6, 0) #move a tração
                if current_time - self.start_time >= 4.0:
                    self.state = 1
                    self.start_time = current_time
            case 1:
                self.drive.arcadeDrive(0, 0) #para a tração

class AutonomousTest2:
    """
    Teste 2:
      - Estado 0: começa a girar apenas o shooter por 4 segundos.
      - Estado 1: girar shooter asssist e indexer por 5 segundos.
      - Estado 2: Finaliza (motores parado).
    """
    def __init__(self, drive , shooter, shooter_assist, indexer):
        self.drive          = drive
        self.shooter        = shooter
        self.shooter_assist = shooter_assist
        self.indexer        = indexer
        self.state          = 0
        self.start_time     = 0

    def start(self):
        self.state = 0
        self.start_time = wpilib.Timer.getFPGATimestamp()

    def run(self):
        current_time = wpilib.Timer.getFPGATimestamp()
        match self.state:
            case 0:
                self.shooter.set(ControlMode.PercentOutput, 1.0)#inicia motor do shooter
                if current_time - self.start_time >= 4.0:
                    self.state = 1
                    self.start_time = current_time
            case 1:
                self.shooter_assist(ControlMode.PercentOutput, 1.0)#motor do flap
                self.indexer(ControlMode.PercentOutput, 1.0)#motor do indexer
                if current_time - self.start_time >= 5.0:
                    self.state = 2
                    self.start_time = current_time
            case 2:
                self.shooter.set(ControlMode.PercentOutput, 0.0)#motor do shooter parado
                self.shooter_assist.set(ControlMode.PercentOutput, 0.0)#motor do shooter assist
                self.indexer.set(ControlMode.PercentOutput, 0.0)#motor do indexer 

class AutonomousTest3:
    """
    Teste 1:
      - Estado 0: começa a girar apenas o shooter por 4 segundos.
      - Estado 1: girar shooter asssist e indexer por 5 segundos.
      - Estado 3: movimenta tração para trás e desliga motores dos mecanismos das bolas.
      - Estado 4: Tração se move por 2 segundos a 70% de velocidade.
    """
    def __init__(self, drive , shooter, shooter_assist, indexer):
        self.drive          = drive
        self.shooter        = shooter
        self.shooter_assist = shooter_assist
        self.indexer        = indexer
        self.state          = 0
        self.start_time     = 0

    def start(self):
        self.state = 0
        self.start_time = wpilib.Timer.getFPGATimestamp()

    def run(self):
        current_time = wpilib.Timer.getFPGATimestamp()
        match self.state:
            case 0:
                self.shooter.set(ControlMode.PercentOutput, 1.0)#inicia motor do shooter
                if current_time - self.start_time >= 4.0:
                    self.state = 1
                    self.start_time = current_time
            case 1:
                self.shooter_assist.set(ControlMode.PercentOutput, 1.0)#motor do flap
                self.indexer.set(ControlMode.PercentOutput, 1.0)#motor do indexer
                if current_time - self.start_time >= 5.0:
                    self.state = 2
                    self.start_time = current_time
            case 3:
                self.drive.arcadeDrive(0.6, 0) #move a tração por 4 segundos
                if current_time - self.start_time >= 4.0:
                    self.state = 4
                    self.start_time = current_time
            case 4:
                self.drive.arcadeDrive(0, 0) #para a tração

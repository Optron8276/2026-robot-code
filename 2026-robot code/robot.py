import wpilib
import wpilib.drive
from wpilib import SmartDashboard
from phoenix5 import WPI_TalonSRX, ControlMode
from wpilib.cameraserver import CameraServer

#-------------------------------- DEFININDO MOTORES ----------------------------------------

class TankRobot(wpilib.TimedRobot):
    def robotInit(self):
        # define motores de acordo com o ID do phoenix turner
        # motores da esquerda
        self.left_front  = WPI_TalonSRX(5)
        self.left_back   = WPI_TalonSRX(4)
        
        #motores da direita
        self.right_front = WPI_TalonSRX(6)
        self.right_back  = WPI_TalonSRX(7)

        #motor do shooter
        self.shooter = WPI_TalonSRX(1)

        #motor mecanismo do intake
        self.intake_esquerda = WPI_TalonSRX(3)
        self.intake_direita = WPI_TalonSRX(8)

        #motor do intake
        self.intake = WPI_TalonSRX(2)

        #motor indexer (talon ainda nao esta na parte eletrica)
        self.indexer = WPI_TalonSRX(9)

        #define o controle do robo como de xbox
        self.controller = wpilib.XboxController(0)

#-------------------------------------------------------------------------------------
        
        #define motores da esquerda
        self.left = wpilib.MotorControllerGroup(self.left_front, self.left_back)
        #define motres da direita 
        self.right = wpilib.MotorControllerGroup(self.right_front, self.right_back)

        #inverter os motores da direita
        self.right.setInverted(True)

        #cria a tração
        self.drive = wpilib.drive.DifferentialDrive(self.left, self.right)
        #modo de segurança (desativado
        self.drive.setSafetyEnabled(False)

        #junta os 2 motores do intake em 1 so mecanismo
        self.mecanismo_intake = wpilib.MotorControllerGroup(
            self.intake_direita, self.intake_esquerda
        )

        #inverte um motor do mecanismo
        self.intake_direita.setInverted(True)

#--------------------------------------------------------------------------------
     
        # garante que o shooter e intake comecem parados(robotinit)
        self.shooter.set(ControlMode.PercentOutput, 0.0)
        self.intake.set(ControlMode.PercentOutput, 0.0)
        self.intake_direita.set(ControlMode.PercentOutput, 0.0)
        self.intake_esquerda.set(ControlMode.PercentOutput, 0.0)
        
        #liga a camera
        CameraServer().launch()
        
#-------------------------------- TELEOPERADO ------------------------------------------

        #faz com que o shooter e inteke iniciem parados(agora no teleoperado)
    def teleopInit(self):
        self.drive.tankDrive(0, 0)
        self.shooter.set(ControlMode.PercentOutput, 0.0)
        self.intake.set(ControlMode.PercentOutput, 0.0)
        self.intake_direita.set(ControlMode.PercentOutput, 0.0)
        self.intake_esquerda.set(ControlMode.PercentOutput, 0.0)

        #pega os valores dos analogicos e os coloca para comandar a tração
    def teleopPeriodic(self):
        speed = -self.controller.getLeftY() #frente / trás
        turn = self.controller.getRightX() #esquerda / direita
        self.drive.arcadeDrive(speed, turn)

        #botoes do mecanismo do intake
        a = self.controller.getAButton()
        b = self.controller.getBButton()

        #se A for presionado mecanismo abre se B for pressionado mecanismo fecha
        if a:
            self.mecanismo_intake.set(1)
        elif b:
            self.mecanismo_intake.set(-1)
        else:
            self.mecanismo_intake.set(0.0)

        #controle do shooter:
        #RT-motor gira para um sentido 
        #RB-motor gira para o outro sentido
        rt = self.controller.getRightTriggerAxis()
        rb = self.controller.getRightBumperButton()

        if rt > 0: #RT controla o shooter de forma proporcional ao quanto aperta
            self.shooter.set(ControlMode.PercentOutput, rt)
        elif rb:
         #RB gira o shooter no sentido contrário
            self.shooter.set(ControlMode.PercentOutput, -1.0)
        else:
            self.shooter.set(ControlMode.PercentOutput, 0.0)


        #controle do intake:
        #LT-intake gira em um sentido 
        #LB-intake gira no sentido contrario
        lt = self.controller.getLeftTriggerAxis()
        lb = self.controller.getLeftBumperButton()

        if lt > 0:
            # LT controla o intake de forma proporcional ao quanto aperta
            self.intake.set(ControlMode.PercentOutput, lt)
        elif lb:
            # LB gira o intake no sentido contrário
            self.intake.set(ControlMode.PercentOutput, -1.0)
        else:
            self.intake.set(ControlMode.PercentOutput, 0.0)


        #controle indexer
        #X-indexer gira em um sentido
        #Y-indexer gira no sentido contrario
        x = self.controller.getXButton()
        y = self.controller.getYButton()

        #se X for presionado mecanismo abre se B for pressionado mecanismo fecha
        if x:
            self.indexer.set (1)
        elif y:
            self.indexer.set (-1)
        else:
            self.indexer.set (0.0)


        #--------------------------- CONFIGURAÇOES DASHBOARD ---------------------------------

        #elastic
        #tempo de partida
        tempo = wpilib.Timer.getMatchTime()
        SmartDashboard.putNumber("tempo de partida", tempo)

        #shooter
        valor_shooter = self.controller.getRightTriggerAxis()
        wpilib.SmartDashboard.putNumber("shooter",valor_shooter)
        #intake
        valor_intake = self.controller.getLeftTriggerAxis()
        wpilib.SmartDashboard.putNumber("intake", valor_intake)
        

if __name__ == "__main__":
    wpilib.run(TankRobot)


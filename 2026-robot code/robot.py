import wpilib
import wpilib.drive
from wpilib import SmartDashboard
from phoenix5 import WPI_TalonSRX, NeutralMode, ControlMode, FeedbackDevice, WPI_VictorSPX
from wpilib.cameraserver import CameraServer
from Autonomo import AutonomousTest1, AutonomousTest2, AutonomousTest3  

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

        #motor mecanismo do intake
        self.intake_esquerda = WPI_TalonSRX(3)
        self.intake_direita = WPI_TalonSRX(8)

        #motor do intake
        self.intake = WPI_TalonSRX(2)

        #motor indexer
        self.indexer = WPI_TalonSRX(9)

        #motor do shooter
        self.shooter = WPI_TalonSRX(1)

        #motor shooter hood com encoder
        self.shooter_hood = WPI_TalonSRX(10)
        # Configura o encoder incremental como sensor de feedback
        self.shooter_hood.configSelectedFeedbackSensor(FeedbackDevice.QuadEncoder, 0, 10)
        # Definir o modo Brake para evitar quedas bruscas
        self.shooter_hood.setNeutralMode(NeutralMode.Brake)
        # Resetar o encoder
        self.shooter_hood.setSelectedSensorPosition(0, 0, 10)
        #garantir que encoder e motor estão na mesma direção
        self.shooter_hood.setSensorPhase(True)

        #eixo com os flaps
        self.shooter_assist = WPI_VictorSPX(11)

        # ----------===---- DEFININDO CONTROLE -----------------------

        #define o controle do robo como de xbox
        self.controller = wpilib.XboxController(0)

        # ----------------------- DRIVE TRAIN ------------------------------
        
        #define motores da esquerda
        self.left = wpilib.MotorControllerGroup(self.left_front, self.left_back)
        #define motres da direita 
        self.right = wpilib.MotorControllerGroup(self.right_front, self.right_back)

        #inverter os motores da direita
        self.right.setInverted(True)

        #cria a tração
        self.drive = wpilib.drive.DifferentialDrive(self.left, self.right)
        #modo de segurança (desativado)
        self.drive.setSafetyEnabled(False)

        # ----------------------- MECANISMO INTAKE -------------------------------

        #junta os 2 motores do intake em 1 so mecanismo
        self.mecanismo_intake = wpilib.MotorControllerGroup(
            self.intake_direita, self.intake_esquerda
        )

        #inverte um motor do mecanismo
        self.intake_direita.setInverted(True)

        # --------------------- ININCIANDO MECANISMOS ----------------------------------
     
        # garante que o shooter e intake comecem parados(robotinit)
        self.shooter.set(ControlMode.PercentOutput, 0.0)
        self.shooter_hood.set(ControlMode.PercentOutput, 0.0)
        self.intake.set(ControlMode.PercentOutput, 0.0)
        self.intake_direita.set(ControlMode.PercentOutput, 0.0)
        self.intake_esquerda.set(ControlMode.PercentOutput, 0.0)
        self.shooter_assist.set(ControlMode.PercentOutput, 0.0)

        #liga a camera
        CameraServer().launch()

        # encoder
        self.position = 0



        
        # Configuração do SendableChooser para selecionar o modo autônomo
        self.auto_chooser = wpilib.SendableChooser()
        self.auto_chooser.setDefaultOption("Tras", "tras")
        self.auto_chooser.addOption("Shooter", "shooter")
        self.auto_chooser.addOption("Shooter-tras", "shooter-tras")
        wpilib.SmartDashboard.putData("Modo Autônomo", self.auto_chooser)
        self.auto_selected = None

        # Cria os objetos autônomos com as lógicas de Frente e frente
        self.auto_test1 = AutonomousTest1(self.drive ,self.shooter, self.shooter_assist, self.indexer)
        self.auto_test2 = AutonomousTest2(self.drive ,self.shooter, self.shooter_assist, self.indexer)
        self.auto_test3 = AutonomousTest3(self.drive ,self.shooter, self.shooter_assist, self.indexer)


    def autonomousInit(self):
        self.auto_selected = self.auto_chooser.getSelected()
        print(f"Modo autônomo selecionado: {self.auto_selected}")
        if self.auto_selected == "tras":
            self.auto_test1.start()
        elif self.auto_selected == "shooter":
            self.auto_test2.start()
        elif self.auto_selected == "shooter-tras":
            self.auto_test3.start()
    
    def autonomousPeriodic(self):
        if self.auto_selected == "tras":
            self.auto_test1.run()
        elif self.auto_selected == "shooter":
            self.auto_test2.run()
        elif self.auto_selected == "shooter-tras":
            self.auto_test3.run()

# ------------------------------- TELEOPINIT --------------------------------------

        #faz com que mecanismos iniciem parados (agora no teleoperado)
    def teleopInit(self):
        self.drive.arcadeDrive(0, 0)
        self.shooter.set(ControlMode.PercentOutput, 0.0)
        self.intake.set(ControlMode.PercentOutput, 0.0)
        self.intake_direita.set(ControlMode.PercentOutput, 0.0)
        self.intake_esquerda.set(ControlMode.PercentOutput, 0.0)

# ----------------------------- TELEOPPERIODIC -------------------------------------
 
        # ------------------------- TRAÇÃO -----------------------------
        #pega os valores dos analogicos e os coloca para comandar a tração
    def teleopPeriodic(self):
        speed = self.controller.getLeftY() #frente / trás
        turn = self.controller.getRightX() #esquerda / direita
        self.drive.arcadeDrive(turn, speed)

        # ------------------------- SHOOTER ------------------------------------

        #controle do SHOOTER:
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

        #motor do flap
        if self.controller.getRawButton(8):
            self.shooter_assist.set(ControlMode.PercentOutput, 1.0)
        else:
            self.shooter_assist.set(ControlMode.PercentOutput, 0.0)


        # ---------------------------------- HOOD SHOOTER --------------------------------------------

        #Controle mecanismo hood SHOOTER
        #seta para cima: mecanismo abre
        #seta para baixo: mecanismo fecha
        #seta para esquerda e direita: posição especifica
        # 
        
            '''     pov = self.controller.getPOV()

            if pov == 90:  # Botão 1 -> comanda o motor para ir até ponto de Pega
                self.shooter_hood.set(ControlMode.Position, 0)
                self.position = 0

            elif pov == 270:  # Botão 2 -> comanda motor para ir até L2
                self.shooter_hood.set(ControlMode.Position, 400)
                self.position = 150
            
            else:
                self.shooter_hood.set(ControlMode.PercentOutput, 0.0)

            if pov == 0:          # seta pra cima
                self.shooter_hood.set(ControlMode.PercentOutput, 0.5)
            elif pov == 180:      # seta pra baixo
                self.shooter_hood.set(ControlMode.PercentOutput, -0.5)

            # ------------------------------ CONTROLE PID HOOD ------------------------------------------------
            if self.shooter_hood.getSelectedSensorPosition(0) <=  self.position:# Aplicar os novos valores ao PID
                    self.shooter_hood.config_kP(0, 2, 10)
                    self.shooter_hood.config_kI(0, 0, 10)
                    self.shooter_hood.config_kD(0, 1, 10)
                    self.shooter_hood.config_kF(0, 0, 10)
                    self.shooter_hood.configClosedLoopPeakOutput(0, 0.7, 10)  #potência máxima permitida definida pela smartdashboard
            
            elif self.shooter_hood.getSelectedSensorPosition(0) >  self.position:
                    self.shooter_hood.config_kP(0, 0.7, 10)
                    self.shooter_hood.config_kI(0, 0, 10)
                    self.shooter_hood.config_kD(0, 0.8, 10)
                    self.shooter_hood.config_kF(0, 0, 10)
                    self.shooter_hood.configClosedLoopPeakOutput(0, 0.8, 10)  #potência máxima permitida definida pela smartdashboard
                    '''

        # -------------------------- INTAKE -----------------------------------
        #botoes do MECANISMO do INTAKE
        a = self.controller.getAButton()
        b = self.controller.getBButton()

        #se A for presionado mecanismo abre se B for pressionado mecanismo fecha
        if a:
            self.mecanismo_intake.set(1)
        elif b:
            self.mecanismo_intake.set(-1)
        else:
            self.mecanismo_intake.set(0.0)
        # nao se usa "ControlMode.PercentOutput" por conta do motorcontrollergroup

        #controle do INTAKE:
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

        # --------------------------- INDEXER -------------------------------------

        #controle indexer
        #X-indexer gira em um sentido
        #Y-indexer gira no sentido contrario
        x = self.controller.getXButton()
        y = self.controller.getYButton()

        #se X for presionado mecanismo abre se y for pressionado mecanismo fecha
        if x:
            self.indexer.set(ControlMode.PercentOutput, 1)
        elif y:
            self.indexer.set(ControlMode.PercentOutput, -1)
        else:
            self.indexer.set (ControlMode.PercentOutput, 0.0)


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
        
        # **Ler posição do encoder**
        self.encoder_position_shooter_hood = self.shooter_hood.getSelectedSensorPosition(0)
        # **Enviar valor do encoder para a Dashboard**
        SmartDashboard.putNumber("Shooter Hood Posição (ticks)", self.encoder_position_shooter_hood)

if __name__ == "__main__":
    wpilib.run(TankRobot)

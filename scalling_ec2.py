import psutil
import boto3 
import time

# Configurações
THRESHOLD_GRADUAL = 60.0  # %
THRESHOLD_IMMEDIATE = 85.0  # %
CHECK_INTERVAL = 5  # segundos
DURATION = 120  # tempo de estresse contínuo
ASG_NAME = 'Plataforma Jornada'
REGION = 'sa-east-1'

# Use variáveis de ambiente ou IAM Role se estiver na EC2
autoscaling = boto3.client('autoscaling', region_name=REGION)

def get_cpu_percent():
    return psutil.cpu_percent(interval=1)

def scale_up():
    try:
        response = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[ASG_NAME])
        group = response['AutoScalingGroups'][0]
        current = group['DesiredCapacity']
        print(f"Escalando: de {current} para {current + 1}")
        autoscaling.update_auto_scaling_group(
            AutoScalingGroupName=ASG_NAME,
            DesiredCapacity=current + 1
        )
    except Exception as e:
        print(f"Erro ao escalar: {e}")

def main():
    start_time = None

    while True:
        cpu = get_cpu_percent()
        print(f"[{time.ctime()}] CPU: {cpu:.2f}%")

        if cpu >= THRESHOLD_IMMEDIATE:
            print("CPU muito alta! Escalando imediatamente...")
            scale_up()
            start_time = None  # reseta o timer
        elif cpu >= THRESHOLD_GRADUAL:
            if start_time is None:
                start_time = time.time()
            elif time.time() - start_time >= DURATION:
                print("CPU alta por tempo prolongado. Escalando...")
                scale_up()
                start_time = None
        else:
            start_time = None

        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()

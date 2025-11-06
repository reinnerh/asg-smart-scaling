import boto3
import sys

# Configurações
ASG_NAME = 'Teste-horarios'          # <--  ASG 
LAUNCH_TEMPLATE_NAME = 'Plataforma-horarios'  # <-- Launch Template 
VERSION_ID_PEQUENO = '2'  # Versão para madrugada (instância menor)
VERSION_ID_GRANDE = '1'   # Versão para horário de pico (instância grande)

region = 'sa-east-1'

# Inicializa cliente
autoscaling = boto3.client('autoscaling', region_name=region)

def update_asg_launch_template(asg_name, launch_template_name, version_id):
    print(f"Atualizando ASG '{asg_name}' para Launch Template '{launch_template_name}' versão '{version_id}'...")
    
    response = autoscaling.update_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        LaunchTemplate={
            'LaunchTemplateName': launch_template_name,
            'Version': version_id
        }
    )
    
    print("Atualização feita com sucesso.")
    return response

def start_instance_refresh(asg_name):
    print(f"Iniciando Instance Refresh no ASG '{asg_name}'...")

    response = autoscaling.start_instance_refresh(
        AutoScalingGroupName=asg_name,
        Preferences={
            'MinHealthyPercentage': 90,  # Mantém 90% de instâncias saudáveis durante refresh
            'InstanceWarmup': 300         # 5 minutos de aquecimento para novas instâncias
        }
    )

    refresh_id = response['InstanceRefreshId']
    print(f"Instance Refresh iniciado com ID: {refresh_id}")
    return refresh_id

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python trocar_instancia_com_refresh.py [pequeno|grande]")
        sys.exit(1)

    perfil = sys.argv[1]

    if perfil == "pequeno":
        update_asg_launch_template(ASG_NAME, LAUNCH_TEMPLATE_NAME, VERSION_ID_PEQUENO)
        start_instance_refresh(ASG_NAME)
    elif perfil == "grande":
        update_asg_launch_template(ASG_NAME, LAUNCH_TEMPLATE_NAME, VERSION_ID_GRANDE)
        start_instance_refresh(ASG_NAME)
    else:
        print("Opção inválida. Use 'pequeno' ou 'grande'.")

from config import app_conf

source_shell = []
target_shell = []
middle_ctr = []


def gen_source_shell():
    middle = app_conf["middle"]
    middle_domain = middle["domain"]
    middle_repo_prefix = middle["repo_prefix"]
    middle_username = middle["username"]
    middle_password = middle["password"]
    source_shell_rename = []
    source_shell_push = []
    global source_shell
    for item in app_conf["source"]:
        # 拉取镜像
        source_shell.append('docker pull %s' % item)
        # 重命名镜像
        ctr_image_convert = item.replace("/", "---").replace(":", "---").replace(".", "--")
        ctr_image_convert = '%s/%s:%s' % (middle_domain, middle_repo_prefix, ctr_image_convert)
        middle_ctr.append(ctr_image_convert)
        source_shell_rename.append('docker tag %s    %s' % (item, ctr_image_convert))
        # 推送镜像
        source_shell_push.append('docker push %s' % ctr_image_convert)
    # 登录镜像仓库
    source_shell.append(
        'docker login %s --username="%s" --password="%s"' % (middle_domain, middle_username, middle_password))
    source_shell += source_shell_rename + source_shell_push
    source_shell.append('')


def gen_target_shell():
    middle = app_conf["middle"]
    middle_domain = middle["domain"]
    middle_username = middle["username"]
    middle_password = middle["password"]
    target = app_conf["target"]
    target_domain = target["domain"]
    target_username = target["username"]
    target_password = target["password"]
    global target_shell
    # 登录中间镜像仓库
    target_shell.append(
        'docker login %s --username="%s" --password="%s"' % (middle_domain, middle_username, middle_password))

    def convert_middle_ctr(target_domain, middle_ctr_name):
        # 例如:
        # 将 docker.io/tanshilindocker/container-image-porter:k8s--gcr--io---sig-storage---csi-attacher---v3--2--1
        # 变成 docker.io/k8s-gcr-io---sig-storage/csi-attacher:v3.2.1
        middle_ctr_name = middle_ctr_name[middle_ctr_name.rfind(":") + 1:]
        middle_ctr_name_part_list = middle_ctr_name.split("---")
        middle_ctr_name = middle_ctr_name_part_list[0] + "---" + middle_ctr_name_part_list[1] + "/"
        middle_ctr_name += middle_ctr_name_part_list[2] + ":"
        middle_ctr_name += middle_ctr_name_part_list[3].replace("--", ".")
        return target_domain + "/" + middle_ctr_name

    target_shell_tag = []
    target_shell_push = []
    for item in middle_ctr:
        # 拉取镜像
        target_shell.append('docker pull %s' % item)
        # 重命名镜像
        ctr_image_convert = convert_middle_ctr(target_domain, item)
        target_shell_tag.append('docker tag %s    %s' % (item, ctr_image_convert))
        # 推送镜像
        target_shell_push.append('docker push %s' % ctr_image_convert)
    # 登录目标镜像仓库
    target_shell.append(
        'docker login %s --username="%s" --password="%s"' % (target_domain, target_username, target_password))
    target_shell += target_shell_tag
    target_shell += target_shell_push
    target_shell.append('')


def gen_shell():
    gen_source_shell()
    gen_target_shell()


if __name__ == '__main__':
    gen_shell()
    print("# 移动源仓库镜像到中间仓库的指令如下: ")
    for item in source_shell:
        print(item)
    print("# 移动中间仓库镜像到目标仓库的指令如下: ")
    for item in target_shell:
        print(item)

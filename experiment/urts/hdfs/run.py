import os, shutil, time
cur_path = os.getcwd()
project_url = "https://github.com/apache/hadoop.git"
project_root_path = os.path.join(cur_path, "hadoop")
project_module_name = "hadoop-hdfs-project/hadoop-hdfs"
project_module_path = os.path.join(project_root_path, project_module_name)
module_pom_file_path = os.path.join(project_module_path, "pom.xml")
api_file_path = os.path.join(project_root_path, "hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configuration.java")
api_pom_file_path = os.path.join(project_root_path, "hadoop-common-project/hadoop-common/pom.xml")
hdfs_api_file_path = os.path.join(project_root_path, "hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HdfsConfiguration.java")
test_copied_path = os.path.join(project_module_path, "src/test/java/org/apache/hadoop")
ctest_configuration_file_path = os.path.join(project_module_path, "src/main/resources/hdfs-ctest.xml")
time_file_path = os.path.join(cur_path, "time.txt")
test_class_num_file_path = os.path.join(cur_path, "test_class_num.txt")
mvn_cmd = "mvn urts:urts -DfailIfNoTests=false |& tee out.txt"
commits = ["1576f81dfe0156514ec06b6051e5df7928a294e2", "c665ab02ed5c400b0c5e9e350686cd0e5b5e6972", "028ec4704b9323954c091bcda3433f7b79cb61de", "832a3c6a8918c73fa85518d5223df65b48f706e9", "3fdeb7435add3593a0a367fff6e8622a73ad9fa3", "98a74e23514392dc8859f407cd40d9c96d8c5923", "1abd03d68f4f236674ce929164cc460037730abb", "8ce30f51f999c0a80db53a2a96b5be5505d4d151", "bce14e746b3d00e692820f28b72ffe306f74d0b2", "b8ab19373d1a291b5faa9944e545b6d5c812a6eb", "b38b00e52839911ab4e0b97fd269c53bf7d1380f", "59fc4061cb619c85538277588f326469dfa08fb8", "4a26a61ecd54bd36b6d089f999359da5fca16723", "f4b24c68e76df40d55258fc5391baabfa9ac362d", "c748fce17ace8b45ee0f3c3967d87893765eea61", "a2a0283c7be8eac641a256f06731cb6e4bab3b09", "762a83e044b84250c6e2543e02f48136361ea3eb", "a1a318417105f155ed5c9d34355309775eb43d11", "eefa664fea1119a9c6e3ae2d2ad3069019fbd4ef", "4ef27a596fd1d7be5e437ab444b12fe450e79e79"]
configuration_file = ["core-default.xml", "prod1.xml", "prod2.xml"]


# Clone testing project
def clone():
    if os.path.exists(project_root_path):
        shutil.rmtree(project_root_path)
    clone_cmd = "git clone " + project_url
    os.system(clone_cmd)


# Record the experiment time
def record_time(elapsed_time, curConfig, curCommit):
    with open(time_file_path, 'a') as f:
        f.write("{}-{} : {}s\n".format(curConfig, curCommit, elapsed_time))


def record_test_class_number(curConfig, curCommit):
    os.chdir(project_module_path)
    p = os.popen("grep 'Tests ' out.txt | sed -e 's/^.*Tests //' -e 's/.\[0;1;32m//' -e 's/.\[m//' -e 's/.\[1m//' -e 's/.\[0;1m//g' -e 's/.\[m//g' | sed -n 's/run: \([1-9][0-9]*\),.*- in \(.*\)/\2     \1/p' | wc -l")
    with open(test_class_num_file_path, 'a') as f:
        f.write("{}-{} : {}\n".format(curConfig, curCommit, int(p.read())))
    os.chdir(cur_path)


# Modify Get/Set API
def modify_api():
    lines = []
    successInsert = False
    with open(hdfs_api_file_path, 'r') as f:
        for line in f:
            lines.append(line)
    
    with open(hdfs_api_file_path, 'w') as f:
        for line in lines:
            f.write(line)
            if "Configuration.addDefaultResource(\"hdfs-rbf-site.xml\");" in line:
                f.write("    Configuration.addDefaultResource(\"hdfs-ctest.xml\"); //UNIFY_TESTS\n")
                successInsert = True
    
    if not successInsert:
        lines = []
        with open(hdfs_api_file_path, 'r') as f:
            for line in f:
                lines.append(line)

        with open(hdfs_api_file_path, 'w') as f:
            for line in lines:
                f.write(line)
                if "Configuration.addDefaultResource(\"hdfs-site.xml\");" in line:
                    f.write("    Configuration.addDefaultResource(\"hdfs-ctest.xml\"); //UNIFY_TESTS\n")
                    successInsert = True
    
    if not successInsert:
        raise ValueError("Can't insert into HDFSConfiguration.java ")
    
    lines = []
    with open(api_file_path, 'r') as f:
        for line in f:
            lines.append(line)

    with open(api_file_path, 'w') as f:
        inGetFunc = False
        inGetDefFunc = False
        inSetFuc = False
        for line in lines:
            if "package org.apache.hadoop.conf;" in line:
                f.write(line)
                f.write("\nimport org.urts.configAware.*;\n")

            # Instrument get(name) or getRaw(name)
            elif "public String get(String name) {" in line or "public String getRaw(String name) {" in line:
                inGetFunc = True
                f.write(line)
                f.write("    String unifyParam = name; //UNIFY_TESTS\n")
            elif inGetFunc:
                if "for(String n : names) {" in line:
                    f.write(line)
                    f.write("      unifyParam = n; //UNIFY_TESTS\n")
                elif "return result;" in line:
                    f.write("    ConfigListener.recordGetConfig(unifyParam, result); //UNIFY_TESTS\n")
                    f.write(line)
                    inGetFunc = False
                else:
                    f.write(line)

            # Instrument get(name, defaultValue)
            elif "public String get(String name, String defaultValue) {" in line:
                inGetDefFunc = True
                f.write(line)
                f.write("    String unifyParam = name; //UNIFY_TESTS\n")
                f.write("    Boolean defaultFlag = true; //UNIFY_TESTS\n")
            elif inGetDefFunc:
                if "for(String n : names) {" in line:
                    f.write(line)
                    f.write("      unifyParam = n; //UNIFY_TESTS\n")
                elif "result = substituteVars(getProps().getProperty(n, defaultValue));" in line:
                    f.write(line)
                    f.write("      if (getProps().getProperty(n) != null) {defaultFlag = false;}\n")
                elif "return result;" in line:
                    f.write(
                        "    if (defaultFlag) { ConfigListener.recordGetConfig(unifyParam, result + \"@DEFAULTVALUE4CONFIGAWARE@\"); }\n")
                    f.write("    else { ConfigListener.recordGetConfig(unifyParam, result); }\n")
                    f.write(line)
                    inGetDefFunc = False
                else:
                    f.write(line)

            # Instrument set()
            elif "public void set(String name, String value, String source) {" in line:
                inSetFuc = True
                f.write(line)
            elif inSetFuc:
                if "name = name.trim();" in line:
                    f.write(line)
                    f.write("    ConfigListener.recordSetConfig(name, value); //UNIFY_TESTS\n")
                elif "if(!n.equals(name)) {" in line:
                    f.write(line)
                    f.write("            ConfigListener.recordSetConfig(name, value); //UNIFY_TESTS\n")
                elif "for(String n : names) {" in line:
                    f.write(line)
                    f.write("        ConfigListener.recordSetConfig(name, value); //UNIFY_TESTS\n")
                    inSetFuc = False
                else:
                    f.write(line)
            else:
                f.write(line)


# Add uRTS to pom file
def modify_pom():
    plugin = "<plugin>\n" \
             "<groupId>org.urts</groupId>\n" \
             "<artifactId>urts-maven-plugin</artifactId>\n" \
             "<version>1.0.0-SNAPSHOT</version>\n" \
             "</plugin>\n"
    lines = []
    meet_plugins = False
    with open(module_pom_file_path, 'r') as f:
        for line in f:
            lines.append(line)

    with open(module_pom_file_path, 'w') as f:
        for line in lines:
            f.write(line)
            if "<plugins>" in line:
                meet_plugins = True
                f.write(plugin)

    dependency = "<dependency>\n" \
                 "<groupId>org.urts</groupId>\n" \
                 "<artifactId>org.urts.core</artifactId>\n" \
                 "<version>1.0.0-SNAPSHOT</version>\n" \
                 "<scope>compile</scope>\n" \
                 "</dependency>\n"
    lines = []
    meet_dependencies = False
    with open(api_pom_file_path, 'r') as f:
        for line in f:
            lines.append(line)

    with open(api_pom_file_path, 'w') as f:
        for line in lines:
            f.write(line)
            if "<dependencies>" in line:
                meet_dependencies = True
                f.write(dependency)

    if not meet_plugins or not meet_dependencies:
        raise ValueError("Failed to modify pom file, has <plugins>? " + str(meet_plugins) + " has <dependencies>? " + str(meet_dependencies))


# Run tests
def run_urts(config_file, curConfig, curCommit):
    os.chdir(project_module_path)
    shutil.copy(config_file, ctest_configuration_file_path)
    print("=================[uRTS: RUN TestGetConfigValueForConfigAware]=================", flush=True)
    start1 = time.time()
    os.system("mvn test -Dtest=TestGetConfigValueForConfigAware")
    end1 = time.time()
    shutil.copy(os.path.join(cur_path, "hdfs-ctest.xml"), ctest_configuration_file_path)
    print("=================[uRTS: RUN uRTS]=================", flush=True)
    start2 = time.time()
    os.system(mvn_cmd)
    end2 = time.time()
    record_time(end1-start1+end2-start2, curConfig, curCommit)
    os.chdir(cur_path)


# Install dependency module
def maven_install_module():
    os.chdir(project_root_path)
    os.system("mvn install -DskipTests  -Denforcer.skip=true -am -pl " + project_module_name)
    os.chdir(cur_path)


# Prepare config file
def copy_production_config_file(replaced_config_file_path, original_config_file_path):
    shutil.copy(replaced_config_file_path, original_config_file_path)


# Prepare uRTS config file
def prepare_urtsrc_file(config_name):
    source_path = os.path.join(cur_path, ".urtsrc-" + config_name)
    target_path = os.path.join(project_module_path, ".urtsrc")
    shutil.copy(source_path, target_path)


# Checkout to certain version
def checkout_commit(commit):
    os.chdir(project_root_path)
    os.system("git checkout -f " + commit)
    os.chdir(cur_path)


# Prepare test that used to get config values
def copy_get_config_value_test():
    print(test_copied_path)
    source_path = os.path.join(cur_path, "TestGetConfigValueForConfigAware.java")
    target_path = os.path.join(test_copied_path, "TestGetConfigValueForConfigAware.java")
    shutil.copy(source_path, target_path)


# Prepare mapping
def copy_ctest_mapping():
    source_path = os.path.join(cur_path, "mapping")
    target_path = os.path.join(project_module_path, "mapping")
    shutil.copy(source_path, target_path)


# Prepare injection file
def create_empty_config_file_for_running_ctest():
    source_path = os.path.join(cur_path, "hdfs-ctest.xml")
    shutil.copy(source_path, ctest_configuration_file_path)


# Prepare environment and all files
def do_preparation(commit):
    checkout_commit(commit)
    modify_pom()
    modify_api()
    copy_ctest_mapping()
    create_empty_config_file_for_running_ctest()
    copy_get_config_value_test()
    maven_install_module()


def run():
    clone()
    for i in range(len(commits)):
        curCommit = commits[i]
        do_preparation(curCommit)
        for curConfig in configuration_file:
            cur_config_name = curConfig.split(".")[0]
            config_file_name = curConfig + "-" + curCommit
            print("===============[uRTS: Evaluation: " + curCommit + " Config: " + cur_config_name + " ]===============", flush=True)
            replacedConfigFilePath = os.path.join(cur_path, "../../config_files/hdfs/", config_file_name)
            targetConfigFilePath = os.path.join(project_module_path, curConfig)
            if not os.path.exists(replacedConfigFilePath):
                ValueError("Does not have configuration file: " + replacedConfigFilePath)
            copy_production_config_file(replacedConfigFilePath, targetConfigFilePath)
            prepare_urtsrc_file(cur_config_name)
            run_urts(replacedConfigFilePath, curConfig, curCommit)
            record_test_class_number(curConfig, curCommit)


if __name__ == '__main__':
    run()

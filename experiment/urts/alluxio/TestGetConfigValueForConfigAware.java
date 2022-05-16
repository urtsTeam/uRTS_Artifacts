package alluxio;

import alluxio.conf.AlluxioProperties;
import alluxio.conf.InstancedConfiguration;
import alluxio.conf.PropertyKey;
import org.junit.Test;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;


public class TestGetConfigValueForConfigAware {
    @Test
    public void testAllConfig() {
        AlluxioProperties mProperties = new AlluxioProperties();
        InstancedConfiguration ic = new InstancedConfiguration(mProperties);
        Map<String, String> configMap = new HashMap<String, String>();
        Field allFiled [] = PropertyKey.class.getDeclaredFields();
        for (Field f : allFiled) {
            if (Modifier.isFinal(f.getModifiers()) && Modifier.isStatic(f.getModifiers()) && Modifier.isPublic(f.getModifiers()) && f.getType().equals(PropertyKey.class)) {
                String name = "";
                String value1 = "null";
                String value2 = "null";
                try {
                    PropertyKey key = (PropertyKey) f.get(PropertyKey.class);
                    name = key.getName();
                    value1 = mProperties.get((PropertyKey) f.get(PropertyKey.class));
                    value2 = ic.get((PropertyKey) f.get(PropertyKey.class));
                } catch (Exception e){
                    value2 = "null";
                }
                if (!name.equals("")) {
                    if (Objects.equals(value1, value2)) {
                        configMap.put(name, value1);
                    } else {
                        configMap.put(name, value1 + "@CONFIGAWARESEPARATOR@" + value2);
                    }
                }
            }
        }
        try {
            File f = new File("../.ConfigValue");
            if (f.exists()) {
                File oldFile = new File(".OldConfigValue");
                if (oldFile.exists()) {
                    oldFile.delete();
                }
                f.renameTo(oldFile);
                f.delete();
            }
            FileWriter myWriter = new FileWriter("../.ConfigValue", true);
            BufferedWriter bufferWriter = new BufferedWriter(myWriter);
            for (Map.Entry<String, String> entry : configMap.entrySet()) {
                bufferWriter.write(entry.getKey() + "=CONFIGAWARE=" + entry.getValue() + "@CONFIGAWARE@\n");
            }
            bufferWriter.close();
        } catch (IOException e){
            e.printStackTrace();
        }
    }
}

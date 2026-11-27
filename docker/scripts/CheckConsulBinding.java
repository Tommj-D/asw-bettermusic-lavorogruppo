import java.util.List;
import org.springframework.boot.context.properties.bind.Binder;
import org.springframework.boot.context.properties.bind.Bindable;
import org.springframework.cloud.client.serviceregistry.AutoServiceRegistrationProperties;
import org.springframework.cloud.commons.util.InetUtils;
import org.springframework.cloud.commons.util.InetUtilsProperties;
import org.springframework.cloud.consul.discovery.ConsulDiscoveryProperties;
import org.springframework.cloud.consul.discovery.HeartbeatProperties;
import org.springframework.cloud.consul.serviceregistry.ConsulAutoRegistration;
import org.springframework.context.support.GenericApplicationContext;

/** Offline contract check using the actual Spring libraries, without a Consul server. */
public class CheckConsulBinding {
    public static void main(String[] args) throws Exception {
        // Interface enumeration is irrelevant to explicit Docker hostnames and may
        // be denied in restricted environments. Stub only this default lookup.
        try (var inet = new InetUtils(new InetUtilsProperties()) {
            @Override public HostInfo findFirstNonLoopbackHostInfo() {
                var info = new HostInfo();
                info.setHostname("unused-default");
                info.setIpAddress("127.0.0.1");
                return info;
            }
        }; var context = new GenericApplicationContext()) {
            var props = new ConsulDiscoveryProperties(inet);
            Binder.get(context.getEnvironment()).bind("spring.cloud.consul.discovery", Bindable.ofInstance(props));
            props.setPort(8080);
            var app = args[0].equals("api-gateway") ? "apigateway" : args[0];
            context.getEnvironment().getSystemProperties().put("spring.application.name", app);
            context.refresh();
            var registration = ConsulAutoRegistration.registration(new AutoServiceRegistrationProperties(),
                props, context, List.of(), List.of(), new HeartbeatProperties());
            var service = registration.getService();
            if (!args[0].equals(service.getAddress()) || !app.equals(service.getName())
                || !(app + "-docker").equals(service.getId()) || service.getPort() != 8080
                || props.isPreferIpAddress() || props.isPreferAgentAddress() || !props.isQueryPassing()
                || !"5s".equals(service.getCheck().getTimeout())
                || service.getCheck().getDeregisterCriticalServiceAfter() != null
                || !("http://" + args[0] + ":8080/actuator/health").equals(service.getCheck().getHttp())) {
                throw new AssertionError("Unexpected registration: " + service);
            }
            System.out.println("PASS Spring Consul registration contract: " + service.getName()
                + " -> " + service.getAddress() + ":8080, " + service.getCheck().getHttp());
        }
    }
}

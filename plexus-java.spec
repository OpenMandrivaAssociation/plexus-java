Name:		plexus-java
Version:	1.5.0
Release:	1
Summary:	Java language support for Plexus
Group:		Development/Java
License:	ASL 2.0
URL:		https://codehaus-plexus.github.io/plexus-languages/
Source0:	https://github.com/codehaus-plexus/plexus-languages/archive/refs/tags/plexus-languages-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
# asm-commons 7.1 provides the same cap and a conflicting jar.
BuildRequires:	mvn(org.ow2.asm:asm) >= 9
BuildRequires:	mvn(com.thoughtworks.qdox:qdox)
# optional in the POM, but the sources import Named and Singleton
BuildRequires:	mvn(javax.inject:javax.inject)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
Reads Java module descriptors and class-file versions. The Maven
Javadoc plugin uses it to place javadoc on the module path. QDox
2.1.0 already has the four model classes this release imports.

%prep
%autosetup -n plexus-languages-plexus-languages-%{version}
# plexus-languages is a one-module reactor whose parent POM is not packaged.
rm -rf src
mv plexus-java/src src
mv plexus-java/pom.xml pom.xml
python - <<PY
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def local(tag):
    return tag.split("}", 1)[-1]

tree = ET.parse("pom.xml")
root = tree.getroot()
for node in list(root):
    if local(node.tag) == "parent":
        root.remove(node)

def ensure(name, text, after):
    for node in root:
        if local(node.tag) == name:
            node.text = text
            return
    el = ET.Element("{%s}%s" % (NS, name))
    el.text = text
    idx = 0
    for i, node in enumerate(list(root)):
        if local(node.tag) in after:
            idx = i + 1
    root.insert(idx, el)

ensure("groupId", "org.codehaus.plexus", ("modelVersion",))
ensure("version", "%{version}", ("artifactId", "groupId", "modelVersion"))
# JDK 9+ activates a profile that compiles module-info.java. That
# descriptor requires the ASM jar as the module org.objectweb.asm, and
# the system jar is not that module. The classpath classes are enough.
for node in list(root):
    if local(node.tag) == "profiles":
        root.remove(node)
tree.write("pom.xml", encoding="utf-8", xml_declaration=True)
PY
rm -rf src/main/java9 plexus-java

%files -f .mfiles
%doc README.md

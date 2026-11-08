Name:		plexus-java
Version:	1.7.0
Release:	1
Summary:	Java language support for Plexus
Group:		Development/Java
License:	ASL 2.0
URL:		https://codehaus-plexus.github.io/plexus-languages/
Source0:	https://github.com/codehaus-plexus/plexus-languages/archive/refs/tags/plexus-languages-%{version}.tar.gz#/plexus-languages-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	mvn(com.github.javaparser:javaparser-core)
BuildRequires:	javaparser-core >= 3.28.2
Requires:	javaparser-core >= 3.28.2
# optional in the POM, but LocationManager imports Named and Singleton
BuildRequires:	mvn(javax.inject:javax.inject)
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
Reads Java module descriptors and class-file versions. Source
descriptors are parsed with JavaParser. Class-file descriptors are
read without ASM, including class-file versions newer than any one
ASM release. A caller can select the multi-release descriptor for a
target release. The JDK 9 module overlay is not packaged.

%prep
%autosetup -n plexus-languages-plexus-languages-%{version}
# The module parent is this reactor, not a published POM.
rm -rf src
mv plexus-java/src src
rm -rf plexus-java src/main/java9
# The JDK 9 profile compiles module-info.java. That descriptor requires
# JavaParser as the named module com.github.javaparser.core, and this
# JavaParser jar is not that module. The classpath classes are enough.
python - <<'PY'
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def tag(name):
    return "{" + NS + "}" + name

def add(parent, name, text):
    node = ET.SubElement(parent, tag(name))
    node.text = text
    return node

root = ET.Element(tag("project"))
add(root, "modelVersion", "4.0.0")
add(root, "groupId", "org.codehaus.plexus")
add(root, "artifactId", "plexus-java")
add(root, "version", "%{version}")
add(root, "name", "Plexus Languages :: Java")
props = ET.SubElement(root, tag("properties"))
add(props, "maven.compiler.release", "8")
add(props, "project.build.sourceEncoding", "UTF-8")
deps = ET.SubElement(root, tag("dependencies"))
for group, artifact, version, optional in (
    ("com.github.javaparser", "javaparser-core", "3.28.2", False),
    ("javax.inject", "javax.inject", "1", True),
):
    dep = ET.SubElement(deps, tag("dependency"))
    add(dep, "groupId", group)
    add(dep, "artifactId", artifact)
    add(dep, "version", version)
    if optional:
        add(dep, "optional", "true")
ET.ElementTree(root).write("pom.xml", encoding="utf-8", xml_declaration=True)
PY

%files -f .mfiles
%doc README.md

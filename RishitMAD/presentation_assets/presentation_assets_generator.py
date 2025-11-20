import graphviz
import os

# --- Configuration ---
ASSETS_DIR = 'presentation_assets'
os.makedirs(ASSETS_DIR, exist_ok=True)

# --- Common Styles ---
GRAPH_ATTR = {
    'splines': 'ortho',
    'pad': '1',
    'nodesep': '0.8',
    'ranksep': '1',
    'fontname': 'Helvetica',
    'fontsize': '20',
    'fontcolor': '#2D3436'
}
NODE_ATTR = {
    'fontname': 'Helvetica',
    'fontsize': '14',
    'shape': 'record',
    'style': 'rounded,filled',
    'fillcolor': '#FFFFFF',
    'color': '#B2BEC3'
}
EDGE_ATTR = {
    'fontname': 'Helvetica',
    'fontsize': '12',
    'color': '#636E72',
    'arrowsize': '0.8'
}

def apply_styles(dot):
    """Applies a consistent set of styles to a graphviz graph."""
    dot.graph_attr.update(GRAPH_ATTR)
    dot.node_attr.update(NODE_ATTR)
    dot.edge_attr.update(EDGE_ATTR)
    return dot

# --- Diagram Generation Functions ---

def generate_use_case_diagram():
    """
    Generates an enhanced Use Case Diagram.
    - Uses standard UML shapes (ovals for use cases, stick figures for actors).
    - Shows relationships between use cases like <<include>>.
    - Organizes the layout for better readability.
    """
    dot = graphviz.Digraph('use_case', comment='Use Case Diagram')
    dot = apply_styles(dot)
    dot.attr(label='Use Case Diagram', labelloc='t', rankdir='TB')

    # Actors
    with dot.subgraph() as s:
        s.attr(rank='source')
        s.node('Admin', 'Admin', shape='egg', fillcolor='#DFF9FB')
        s.node('Doctor', 'Doctor', shape='egg', fillcolor='#DFF9FB')
        s.node('Patient', 'Patient', shape='egg', fillcolor='#DFF9FB')

    # System Boundary
    with dot.subgraph(name='cluster_system') as c:
        c.attr(label='Hospital Management System', style='rounded,dashed', color='grey')
        c.attr('node', shape='ellipse', style='filled', fillcolor='#E0E0E0')
        
        # Use Cases
        c.node('UC_MANAGE_USERS', 'Manage Users & Depts.')
        c.node('UC_ANALYTICS', 'View Analytics')
        c.node('UC_MANAGE_AVAIL', 'Manage Availability')
        c.node('UC_UPDATE_HISTORY', 'Update Patient Records')
        c.node('UC_VIEW_HISTORY', 'View Medical History')
        c.node('UC_BOOK_APPT', 'Book / Cancel Appointments')
        c.node('UC_SEARCH', 'Search & View Doctors')
        c.node('UC_MANAGE_PROFILE', 'Manage Profile')
        c.node('UC_LOGIN', 'Login')

    # Relationships
    dot.edge('Admin', 'UC_MANAGE_USERS')
    dot.edge('Admin', 'UC_ANALYTICS')
    dot.edge('Admin', 'UC_LOGIN')

    dot.edge('Doctor', 'UC_MANAGE_AVAIL')
    dot.edge('Doctor', 'UC_UPDATE_HISTORY')
    dot.edge('Doctor', 'UC_VIEW_HISTORY')
    dot.edge('Doctor', 'UC_LOGIN')

    dot.edge('Patient', 'UC_MANAGE_PROFILE')
    dot.edge('Patient', 'UC_SEARCH')
    dot.edge('Patient', 'UC_BOOK_APPT')
    dot.edge('Patient', 'UC_VIEW_HISTORY')
    dot.edge('Patient', 'UC_LOGIN')
    
    # <<include>> relationship - **THIS IS THE FIX**
    dot.edge('UC_BOOK_APPT', 'UC_SEARCH', label='<<include>>', style='dashed', arrowhead='open')

    file_path = os.path.join(ASSETS_DIR, 'use_case_diagram_enhanced')
    dot.render(file_path, format='png', view=False, cleanup=True)
    print(f"Generated: {file_path}.png")


def generate_db_schema_diagram():
    """
    Generates a detailed Database Schema (ER Diagram).
    - Uses HTML-like labels for detailed table structures.
    - Clearly marks Primary Keys (PK) and Foreign Keys (FK).
    - Uses crow's foot notation to show one-to-many relationships.
    """
    dot = graphviz.Digraph('db_schema', comment='Database Schema')
    dot = apply_styles(dot)
    dot.attr(label='Database Schema (ER Diagram)', labelloc='t', rankdir='LR')
    dot.attr('node', shape='plain')

    # Table Definitions using HTML-like labels for structure
    tables = {
        'User': '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
                      <TR><TD COLSPAN="2" BGCOLOR="#74B9FF"><B>User</B></TD></TR>
                      <TR><TD ALIGN="LEFT">id (PK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                      <TR><TD ALIGN="LEFT">username</TD><TD ALIGN="LEFT">STRING</TD></TR>
                      <TR><TD ALIGN="LEFT">password</TD><TD ALIGN="LEFT">STRING</TD></TR>
                      <TR><TD ALIGN="LEFT">role</TD><TD ALIGN="LEFT">STRING</TD></TR>
                      <TR><TD ALIGN="LEFT">is_blacklisted</TD><TD ALIGN="LEFT">BOOLEAN</TD></TR>
                    </TABLE>>''',
        'Department': '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
                             <TR><TD COLSPAN="2" BGCOLOR="#A29BFE"><B>Department</B></TD></TR>
                             <TR><TD ALIGN="LEFT">id (PK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                             <TR><TD ALIGN="LEFT">name</TD><TD ALIGN="LEFT">STRING</TD></TR>
                             <TR><TD ALIGN="LEFT">description</TD><TD ALIGN="LEFT">TEXT</TD></TR>
                           </TABLE>>''',
        'Doctor': '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
                       <TR><TD COLSPAN="2" BGCOLOR="#55E6C1"><B>Doctor</B></TD></TR>
                       <TR><TD ALIGN="LEFT">id (PK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                       <TR><TD ALIGN="LEFT">user_id (FK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                       <TR><TD ALIGN="LEFT">specialization_id (FK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                       <TR><TD ALIGN="LEFT">name</TD><TD ALIGN="LEFT">STRING</TD></TR>
                       <TR><TD ALIGN="LEFT">qualifications</TD><TD ALIGN="LEFT">STRING</TD></TR>
                       <TR><TD ALIGN="LEFT">experience</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                     </TABLE>>''',
        'Patient': '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
                        <TR><TD COLSPAN="2" BGCOLOR="#55E6C1"><B>Patient</B></TD></TR>
                        <TR><TD ALIGN="LEFT">id (PK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                        <TR><TD ALIGN="LEFT">user_id (FK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                        <TR><TD ALIGN="LEFT">name</TD><TD ALIGN="LEFT">STRING</TD></TR>
                        <TR><TD ALIGN="LEFT">contact</TD><TD ALIGN="LEFT">STRING</TD></TR>
                      </TABLE>>''',
        'Appointment': '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
                            <TR><TD COLSPAN="2" BGCOLOR="#FAB1A0"><B>Appointment</B></TD></TR>
                            <TR><TD ALIGN="LEFT">id (PK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                            <TR><TD ALIGN="LEFT">doctor_id (FK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                            <TR><TD ALIGN="LEFT">patient_id (FK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                            <TR><TD ALIGN="LEFT">date</TD><TD ALIGN="LEFT">DATE</TD></TR>
                            <TR><TD ALIGN="LEFT">time</TD><TD ALIGN="LEFT">TIME</TD></TR>
                            <TR><TD ALIGN="LEFT">status</TD><TD ALIGN="LEFT">STRING</TD></TR>
                          </TABLE>>''',
        'Treatment': '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
                          <TR><TD COLSPAN="2" BGCOLOR="#FFEAA7"><B>Treatment</B></TD></TR>
                          <TR><TD ALIGN="LEFT">id (PK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                          <TR><TD ALIGN="LEFT">appointment_id (FK)</TD><TD ALIGN="LEFT">INTEGER</TD></TR>
                          <TR><TD ALIGN="LEFT">visit_type</TD><TD ALIGN="LEFT">STRING</TD></TR>
                          <TR><TD ALIGN="LEFT">diagnosis</TD><TD ALIGN="LEFT">TEXT</TD></TR>
                          <TR><TD ALIGN="LEFT">medicines</TD><TD ALIGN="LEFT">JSON</TD></TR>
                        </TABLE>>'''
    }

    for name, label in tables.items():
        dot.node(name, label)

    # Relationships with Cardinality (Crow's Foot Notation)
    dot.edge('User', 'Doctor', arrowhead='none', arrowtail='teeodot', dir='both', label=' (1..1)')
    dot.edge('User', 'Patient', arrowhead='none', arrowtail='teeodot', dir='both', label=' (1..1)')
    dot.edge('Department', 'Doctor', arrowhead='crowoinv', arrowtail='tee', dir='both', label=' (1..*)')
    dot.edge('Doctor', 'Appointment', arrowhead='crowoinv', arrowtail='tee', dir='both', label=' (1..*)')
    dot.edge('Patient', 'Appointment', arrowhead='crowoinv', arrowtail='tee', dir='both', label=' (1..*)')
    dot.edge('Appointment', 'Treatment', arrowhead='none', arrowtail='teeodot', dir='both', label=' (1..1)')

    file_path = os.path.join(ASSETS_DIR, 'db_schema_diagram_enhanced')
    dot.render(file_path, format='png', view=False, cleanup=True)
    print(f"Generated: {file_path}.png")


def generate_workflow_diagram():
    """
    Generates an improved Workflow Diagram (Flowchart).
    - Includes decision points to show branching logic.
    - Uses different shapes for actions, decisions, and start/end points.
    - Spans multiple actors (Patient, System, Doctor).
    """
    dot = graphviz.Digraph('workflow', comment='Appointment Booking & Completion Workflow')
    dot = apply_styles(dot)
    dot.attr(label='Appointment Booking & Completion Workflow', labelloc='t', rankdir='TB')

    # Define shapes
    dot.attr('node', style='rounded,filled')
    start_end_shape = {'shape': 'ellipse', 'fillcolor': '#ffeaa7'}
    patient_action_shape = {'shape': 'box', 'fillcolor': '#DFF9FB'}
    doctor_action_shape = {'shape': 'box', 'fillcolor': '#d4edda'}
    system_process_shape = {'shape': 'box', 'fillcolor': '#e2e3e5'}
    decision_shape = {'shape': 'diamond', 'fillcolor': '#fab1a0'}

    # Nodes
    dot.node('START', 'Patient Logs In', **start_end_shape)
    dot.node('A', 'Views Dashboard & Selects Department', **patient_action_shape)
    dot.node('B', 'Views Doctor Profile', **patient_action_shape)
    dot.node('C', 'Checks Availability', **patient_action_shape)
    dot.node('D', 'Slot Available?', **decision_shape)
    dot.node('E', 'Selects & Books Slot', **patient_action_shape)
    dot.node('F', 'System Creates Appointment (Status: Booked)', **system_process_shape)
    dot.node('G', 'Doctor Logs In & Views Dashboard', **doctor_action_shape)
    dot.node('H', 'Selects Appointment to Update', **doctor_action_shape)
    dot.node('I', 'Fills Treatment Details Form', **doctor_action_shape)
    dot.node('J', 'System Saves Treatment & Updates Status (Completed)', **system_process_shape)
    dot.node('END', 'Patient Can View Updated History', **start_end_shape)

    # Edges
    dot.edge('START', 'A'); dot.edge('A', 'B'); dot.edge('B', 'C'); dot.edge('C', 'D')
    dot.edge('D', 'E', label=' Yes ')
    dot.edge('D', 'B', label=' No, Try Another Dr. ')
    dot.edge('E', 'F'); dot.edge('F', 'G'); dot.edge('G', 'H'); dot.edge('H', 'I')
    dot.edge('I', 'J'); dot.edge('J', 'END')

    file_path = os.path.join(ASSETS_DIR, 'workflow_diagram_enhanced')
    dot.render(file_path, format='png', view=False, cleanup=True)
    print(f"Generated: {file_path}.png")


def generate_deployment_diagram():
    """
    Generates a more detailed Deployment Diagram for a basic setup.
    - Uses standard component and node shapes.
    - Shows artifacts deployed on nodes.
    """
    dot = graphviz.Digraph('deployment', comment='Deployment Diagram')
    dot = apply_styles(dot)
    dot.attr(label='Simple Deployment Diagram', labelloc='t', rankdir='TB')
    
    with dot.subgraph(name='cluster_server') as c:
        c.attr(label='Production Server', style='filled', color='lightgrey')
        c.attr('node', shape='box', style='rounded')
        
        with c.subgraph(name='cluster_wsgi') as w:
            w.attr(label='WSGI Server Node', color='blue')
            w.node('Gunicorn', '<<Component>>\nGunicorn')
        
        with c.subgraph(name='cluster_app') as a:
            a.attr(label='Application Node', color='green')
            a.node('Flask', '<<Component>>\nFlask Application')
            a.node('DBFile', '<<Artifact>>\nhospital.db', shape='note')
            a.edge('Flask', 'DBFile', style='dashed')
            
    dot.node('UserBrowser', 'User Browser', shape='component')
    dot.edge('UserBrowser', 'Gunicorn', label='HTTP/S')
    dot.edge('Gunicorn', 'Flask', label='WSGI')

    file_path = os.path.join(ASSETS_DIR, 'deployment_diagram_enhanced')
    dot.render(file_path, format='png', view=False, cleanup=True)
    print(f"Generated: {file_path}.png")


def generate_scalable_deployment_diagram():
    """
    Generates a Deployment Diagram for a scalable architecture.
    - Introduces a Load Balancer, multiple app instances, and a dedicated database server.
    - Shows a more realistic production setup.
    """
    dot = graphviz.Digraph('scalable_deployment', comment='Scalable Deployment Diagram')
    dot = apply_styles(dot)
    dot.attr(label='Scalable Deployment Architecture', labelloc='t', rankdir='TB')
    
    dot.node('UserBrowser', 'User Browser', shape='component')
    dot.node('LoadBalancer', '<<Component>>\nLoad Balancer\n(e.g., Nginx)', shape='cds')

    with dot.subgraph(name='cluster_app_servers') as c:
        c.attr(label='Application Servers (VMs / Containers)', style='filled', color='lightgrey')
        c.attr('node', shape='box', style='rounded')
        
        for i in range(1, 3): # Create 2 app server instances
            with c.subgraph(name=f'cluster_app_{i}') as s:
                s.attr(label=f'App Server {i}')
                s.node(f'Gunicorn_{i}', 'Gunicorn')
                s.node(f'Flask_{i}', 'Flask App')
                s.edge(f'Gunicorn_{i}', f'Flask_{i}', label='WSGI')

    with dot.subgraph(name='cluster_db') as c:
        c.attr(label='Database Server', style='filled', color='lightblue')
        c.node('PostgreSQL', '<<Component>>\nPostgreSQL DB', shape='cylinder')

    # Edges
    dot.edge('UserBrowser', 'LoadBalancer', label='HTTP/S')
    dot.edge('LoadBalancer', 'Gunicorn_1')
    dot.edge('LoadBalancer', 'Gunicorn_2')
    dot.edge('Flask_1', 'PostgreSQL', label='DB Connection')
    dot.edge('Flask_2', 'PostgreSQL', label='DB Connection')

    file_path = os.path.join(ASSETS_DIR, 'scalable_deployment_diagram')
    dot.render(file_path, format='png', view=False, cleanup=True)
    print(f"Generated: {file_path}.png")


if __name__ == '__main__':
    print("--- Generating Presentation Diagrams ---")
    # generate_use_case_diagram()
    generate_db_schema_diagram()
    generate_workflow_diagram()
    generate_deployment_diagram()
    generate_scalable_deployment_diagram()
    print(f"\nAll diagrams have been saved in the '{ASSETS_DIR}' folder.")
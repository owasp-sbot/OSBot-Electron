from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import uuid

# Create the FastAPI app
app = FastAPI(
    title="MGraph API",
    description="API for interacting with the MGraph database",
    version="1.0.0",
)

# Add CORS middleware to allow requests from the Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models

class NodeBase(BaseModel):
    """Base model for a node in the graph"""
    node_type: str = Field(..., description="Type of the node")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")


class NodeCreate(NodeBase):
    """Model for creating a new node"""
    pass


class Node(NodeBase):
    """Model for a node with ID"""
    node_id: str = Field(..., description="Unique identifier for the node")


class EdgeBase(BaseModel):
    """Base model for an edge in the graph"""
    edge_type: str = Field(..., description="Type of the edge")
    from_node_id: str = Field(..., description="ID of the source node")
    to_node_id: str = Field(..., description="ID of the target node")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties")


class EdgeCreate(EdgeBase):
    """Model for creating a new edge"""
    pass


class Edge(EdgeBase):
    """Model for an edge with ID"""
    edge_id: str = Field(..., description="Unique identifier for the edge")


# In-memory storage for demo purposes
nodes_db = {}
edges_db = {}


# API Routes

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to docs"""
    return {"message": "Welcome to MGraph API. Visit /docs for the API documentation."}


# Node operations

@app.post("/nodes/", response_model=Node, tags=["Nodes"])
async def create_node(node: NodeCreate):
    """Create a new node in the graph"""
    node_id = str(uuid.uuid4())
    node_data = Node(
        node_id=node_id,
        node_type=node.node_type,
        properties=node.properties
    )
    nodes_db[node_id] = node_data
    return node_data


@app.get("/nodes/", response_model=List[Node], tags=["Nodes"])
async def get_nodes(
        node_type: Optional[str] = Query(None, description="Filter nodes by type")
):
    """Get all nodes, optionally filtered by type"""
    if node_type:
        return [node for node in nodes_db.values() if node.node_type == node_type]
    return list(nodes_db.values())


@app.get("/nodes/{node_id}", response_model=Node, tags=["Nodes"])
async def get_node(node_id: str):
    """Get a node by its ID"""
    if node_id not in nodes_db:
        raise HTTPException(status_code=404, detail="Node not found")
    return nodes_db[node_id]


@app.put("/nodes/{node_id}", response_model=Node, tags=["Nodes"])
async def update_node(node_id: str, node: NodeBase):
    """Update a node by its ID"""
    if node_id not in nodes_db:
        raise HTTPException(status_code=404, detail="Node not found")

    existing_node = nodes_db[node_id]
    existing_node.node_type = node.node_type
    existing_node.properties = node.properties

    return existing_node


@app.delete("/nodes/{node_id}", tags=["Nodes"])
async def delete_node(node_id: str):
    """Delete a node by its ID"""
    if node_id not in nodes_db:
        raise HTTPException(status_code=404, detail="Node not found")

    # Delete the node
    del nodes_db[node_id]

    # Delete any edges connected to this node
    edges_to_delete = [edge_id for edge_id, edge in edges_db.items()
                       if edge.from_node_id == node_id or edge.to_node_id == node_id]

    for edge_id in edges_to_delete:
        del edges_db[edge_id]

    return {"message": f"Node {node_id} and its connected edges deleted successfully"}


# Edge operations

@app.post("/edges/", response_model=Edge, tags=["Edges"])
async def create_edge(edge: EdgeCreate):
    """Create a new edge in the graph"""
    # Verify that both nodes exist
    if edge.from_node_id not in nodes_db:
        raise HTTPException(status_code=404, detail=f"Source node {edge.from_node_id} not found")
    if edge.to_node_id not in nodes_db:
        raise HTTPException(status_code=404, detail=f"Target node {edge.to_node_id} not found")

    edge_id = str(uuid.uuid4())
    edge_data = Edge(
        edge_id=edge_id,
        edge_type=edge.edge_type,
        from_node_id=edge.from_node_id,
        to_node_id=edge.to_node_id,
        properties=edge.properties
    )
    edges_db[edge_id] = edge_data
    return edge_data


@app.get("/edges/", response_model=List[Edge], tags=["Edges"])
async def get_edges(
        edge_type: Optional[str] = Query(None, description="Filter edges by type"),
        from_node_id: Optional[str] = Query(None, description="Filter edges by source node"),
        to_node_id: Optional[str] = Query(None, description="Filter edges by target node")
):
    """Get all edges, optionally filtered by type or connected nodes"""
    filtered_edges = list(edges_db.values())

    if edge_type:
        filtered_edges = [edge for edge in filtered_edges if edge.edge_type == edge_type]

    if from_node_id:
        filtered_edges = [edge for edge in filtered_edges if edge.from_node_id == from_node_id]

    if to_node_id:
        filtered_edges = [edge for edge in filtered_edges if edge.to_node_id == to_node_id]

    return filtered_edges


@app.get("/edges/{edge_id}", response_model=Edge, tags=["Edges"])
async def get_edge(edge_id: str):
    """Get an edge by its ID"""
    if edge_id not in edges_db:
        raise HTTPException(status_code=404, detail="Edge not found")
    return edges_db[edge_id]


@app.put("/edges/{edge_id}", response_model=Edge, tags=["Edges"])
async def update_edge(edge_id: str, edge: EdgeBase):
    """Update an edge by its ID"""
    if edge_id not in edges_db:
        raise HTTPException(status_code=404, detail="Edge not found")

    # Verify that both nodes exist
    if edge.from_node_id not in nodes_db:
        raise HTTPException(status_code=404, detail=f"Source node {edge.from_node_id} not found")
    if edge.to_node_id not in nodes_db:
        raise HTTPException(status_code=404, detail=f"Target node {edge.to_node_id} not found")

    existing_edge = edges_db[edge_id]
    existing_edge.edge_type = edge.edge_type
    existing_edge.from_node_id = edge.from_node_id
    existing_edge.to_node_id = edge.to_node_id
    existing_edge.properties = edge.properties

    return existing_edge


@app.delete("/edges/{edge_id}", tags=["Edges"])
async def delete_edge(edge_id: str):
    """Delete an edge by its ID"""
    if edge_id not in edges_db:
        raise HTTPException(status_code=404, detail="Edge not found")

    del edges_db[edge_id]
    return {"message": f"Edge {edge_id} deleted successfully"}


# Graph operations

@app.get("/graph/", tags=["Graph"])
async def get_graph():
    """Get the entire graph structure"""
    return {
        "nodes": list(nodes_db.values()),
        "edges": list(edges_db.values())
    }


@app.post("/graph/clear", tags=["Graph"])
async def clear_graph():
    """Clear all nodes and edges from the graph"""
    nodes_db.clear()
    edges_db.clear()
    return {"message": "Graph cleared successfully"}


if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(app, host="127.0.0.1", port=8000)
import React from 'react';
import VisualizationPanel from './VisualizationPanel';
import { AppBar, Toolbar, Typography, Box, IconButton, Divider, Drawer, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import PanToolIcon from '@mui/icons-material/PanTool';
import FitScreenIcon from '@mui/icons-material/FitScreen';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import TimelineIcon from '@mui/icons-material/Timeline';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import ChangeHistoryIcon from '@mui/icons-material/ChangeHistory';
import LinkIcon from '@mui/icons-material/Link';
import TreeView from '@mui/lab/TreeView';
import TreeItem from '@mui/lab/TreeItem';

// Layout: MenuBar, IconBar, VisualizationPanel, DataPanel
export default function MainLayout() {
  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Menu Bar */}
      <AppBar position="static" color="primary">
        <Toolbar variant="dense">
          <IconButton edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" color="inherit" component="div">
            Linkage2D Web
          </Typography>
        </Toolbar>
      </AppBar>
      {/* Icon Bar */}
      <Box sx={{ display: 'flex', flexDirection: 'row', bgcolor: 'grey.100', p: 1 }}>
        <IconButton><PanToolIcon /></IconButton>
        <IconButton><ZoomInIcon /></IconButton>
        <IconButton><ZoomOutIcon /></IconButton>
        <IconButton><FitScreenIcon /></IconButton>
        <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
        <IconButton><AddCircleOutlineIcon /></IconButton>
        <IconButton><TimelineIcon /></IconButton>
        <IconButton><RadioButtonUncheckedIcon /></IconButton>
        <IconButton><ChangeHistoryIcon /></IconButton>
        <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
        <IconButton><LinkIcon /></IconButton>
      </Box>
      {/* Main Content: Visualization + Data Panel */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'row', minHeight: 0 }}>
        {/* Visualization Panel */}
        <Box sx={{ flex: 3, bgcolor: 'white', border: 1, borderColor: 'grey.300', m: 1, borderRadius: 2, position: 'relative', overflow: 'hidden' }}>
          <VisualizationPanel />
        </Box>
        {/* Data Panel */}
        <Box sx={{ flex: 1, bgcolor: 'grey.50', border: 1, borderColor: 'grey.300', m: 1, borderRadius: 2, minWidth: 250, overflow: 'auto' }}>
          <Typography variant="subtitle1" sx={{ p: 2 }}>Data Panel</Typography>
          <TreeView defaultCollapseIcon={<MinusSquare />} defaultExpandIcon={<PlusSquare />}>
            {/* TODO: Populate with linkage data tree */}
            <TreeItem nodeId="1" label="Linkage">
              <TreeItem nodeId="2" label="Links" />
              <TreeItem nodeId="3" label="Joints" />
            </TreeItem>
          </TreeView>
        </Box>
      </Box>
    </Box>
  );
}

// Placeholder icons for TreeView
function MinusSquare() {
  return <span style={{ display: 'inline-block', width: 14 }}>-</span>;
}
function PlusSquare() {
  return <span style={{ display: 'inline-block', width: 14 }}>+</span>;
}

import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';
import { withStyles, AppBar, Drawer, Toolbar, List, Divider, CssBaseline, Typography, Card, Container, Grid, Box, Link } from '@material-ui/core';
import { mainListItems, secondaryListItems } from './listItems';
import CopyRight from '../../Copyright';
import EditProfile from './EditProfile';
const drawerWidth = 240;

const styles = (theme) => ({
    root: {
        display: 'flex',
    },
    appBar: {
        zIndex: theme.zIndex.drawer + 1,
    },
    drawer: {
        width: drawerWidth,
        flexShrink: 0,
    },
    drawerPaper: {
        width: drawerWidth,
    },
    drawerContainer: {
        overflow: 'auto',
    },
    content: {
        flexGrow: 1,
        padding: theme.spacing(3),
    },
    paper: {
        padding: theme.spacing(2),
        display: 'flex',
        overflow: 'auto',
        flexDirection: 'column',
    },
    fixedHeight: {
        height: 240,
    },
});

class DoctorHome extends Component {
    constructor(props) {
        super(props);
        this.handleLogout = this.handleLogout.bind(this);
        this.renderProfile = this.renderProfile.bind(this);
    }

    handleLogout() {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('creds');
        sessionStorage.removeItem('userData');
        sessionStorage.removeItem('userCategory');
    }


    renderProfile() {

        const { classes } = this.props;

        if (this.props.User.isAuthenticated && this.props.User.category === 'doctor') {
            let userData = JSON.parse(this.props.User.userData);
            return (
                <div className={classes.root}>
                    <CssBaseline />
                    <AppBar position="fixed" className={classes.appBar}>
                        <Toolbar>
                            <Typography variant="h6" noWrap>
                                Doctor
                            </Typography>
                            <Link color='inherit' href='http://localhost:3000/home' onClick={() => { this.handleLogout() }} style={{ marginLeft: 'auto' }}>
                                Logout
                            </Link>
                        </Toolbar>
                    </AppBar>
                    <Drawer
                        className={classes.drawer}
                        variant="permanent"
                        classes={{
                            paper: classes.drawerPaper,
                        }}
                    >
                        <Toolbar />
                        <div className={classes.drawerContainer}>
                            <List>{mainListItems}</List>
                            <Divider />
                            <List>{secondaryListItems}</List>
                        </div>
                    </Drawer>


                    <main className={classes.content}>
                        <Toolbar />
                        <div />
                        <Container maxWidth="lg" >
                            <Grid container spacing={3}>
                                <Grid item xs={12}>
                                    <Card style={{ padding: 20 }}>
                                        <Typography variant='h6'>Dr. {userData.name}</Typography>
                                        <Typography variant='body1'>Email: {userData.email}</Typography>
                                        <Typography variant='body1'>Address: {userData.address}</Typography>
                                        <Typography variant='body1'>Phone number: {userData.phoneNum}</Typography>
                                        <Typography variant='body1'>Date of birth: {userData.date_of_birth}</Typography>
                                        <Typography variant='body1'>Department: {userData.department}</Typography>
                                        <Typography variant='body1'>Designation: {userData.designation}</Typography>
                                        <Typography variant='body1'>Qualification: {userData.qualification}</Typography>
                                        <Typography variant='body1'>Gender: {userData.gender}</Typography>
                                    </Card>

                                    <EditProfile
                                        userData={userData}
                                        User={this.props.User}
                                        updateUser={this.props.updateUser}
                                    />
                                </Grid>
                            </Grid>
                            <Box pt={4}>
                                {CopyRight}
                            </Box>
                        </Container>
                    </main>
                </div>
            );
        }
        else {
            return (<Redirect to='/sign-in' />);
        }
    }

    render() {
        const profile = this.renderProfile();
        return (
            <React.Fragment>
                {profile}
            </React.Fragment>
        );
    }
}

export default withStyles(styles)(DoctorHome);
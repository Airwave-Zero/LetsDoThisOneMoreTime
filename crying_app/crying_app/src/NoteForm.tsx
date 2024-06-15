import {Form, Stack, Row, Col, Button} from "React-bootstrap"
import CreatableReactSelect from "react-select/creatable"
import {Link} from "react-router-dom"
import {useRef, FormEvent} from "react"
import {NoteData} from "./App"


type NoteFormProps = {
    onSubmit: (data: NoteData) => void
}


export function NoteForm( {onSubmit}: NoteFormProps)
{
    const titleRef = useRef<HTMLInputElement>(null)
    const markdownRef = useRef<HTMLTextAreaElement>(null)

    function handleSubmit(e:FormEvent){
        e.preventDefault()

        onSubmit(
        {
            /* That's the non-null assertion operator. It is a way to tell the compiler 
            "this expression cannot be null or undefined here, so don't complain about 
            the possibility of it being null or undefined." Sometimes the type checker 
            is unable to make that determination itself. The bang operator tells the 
            compiler to temporarily relax the "not null" constraint that it might 
            otherwise demand. It says to the compiler: "As the developer, 
            I know better than you that this variable cannot be null right now". */
            title: titleRef.current!.value,
            markdown: markdownRef.current!.value,
            tags:[]
        }
        )
    }
    return (
        <Form onSubmit = {handleSubmit}>
            <Stack gap={4}>
               <Row>
                <Col>
                <Form.Group controlId = "title">
                    <Form.Label>Title</Form.Label>
                    <Form.Control ref = {titleRef} required></Form.Control>
                </Form.Group>
                </Col>
                <Col>
                <Form.Group controlId = "tags">
                    <Form.Label>Tags</Form.Label>
                    <CreatableReactSelect isMulti></CreatableReactSelect>
                </Form.Group>
                </Col>
               </Row>
               <Form.Group controlId = "markdown">
                    <Form.Label>Body</Form.Label>
                    <Form.Control ref = {markdownRef} required as ="textarea"  rows ={15}></Form.Control>
                </Form.Group>
                <Stack direction = "horizontal" gap = {2} className = "justify-content-end">
                    <Button type="submit" variant = "primary">Save</Button>
                    <Link to="..">
                        <Button type="button" variant = "outline-secondary">Cancel</Button>
                    </Link>
                </Stack>
            </Stack>
        </Form>
    )
}